import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Decrypts UAKino app offline downloads (HLS segments) into a single .ts file per episode.
 *
 * Chain:
 *   1) FieldCipher key (32 bytes) = base64 in .download-field.key
 *   2) per-episode ".key" file = AES-256-GCM( base64(16-byte AES-128 segment key) )
 *   3) each segN.ts.enc = AES-128-CBC-PKCS5( segment, key, IV=ivFor(N) )
 */
public class DecryptUAKino {

    static byte[] fieldKey;

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage: DecryptUAKino <fieldKeyFile> <downloadsDir> <outputDir> [onlyEpisodeDir]");
            System.exit(2);
        }
        Path fieldKeyPath = Paths.get(args[0]);
        File downloadsDir = new File(args[1]);
        File outputDir = new File(args[2]);
        String only = args.length > 3 && !args[3].isBlank() ? args[3] : null;

        fieldKey = base64Decode(new String(Files.readAllBytes(fieldKeyPath)).trim());
        if (fieldKey.length != 32) throw new IllegalStateException("FieldCipher key must be 32 bytes, got " + fieldKey.length);

        outputDir.mkdirs();

        File[] eps = downloadsDir.listFiles(File::isDirectory);
        if (eps == null) { System.err.println("No episode dirs in " + downloadsDir); System.exit(1); }
        Arrays.sort(eps, Comparator.comparing(File::getName));

        int done = 0, total = 0;
        for (File ep : eps) {
            if (only != null && !ep.getName().equals(only)) continue;
            total++;
            File out = new File(outputDir, ep.getName() + ".ts");
            decryptEpisode(ep, out);
            done++;
            System.out.println("OK " + ep.getName() + " -> " + out.getName() + " (" + (out.length() / 1048576) + " MB)");
        }
        System.out.println("DONE episodes=" + done + "/" + total);
    }

    static void decryptEpisode(File epDir, File outTs) throws Exception {
        File keyFile = new File(epDir, ".key");
        String keyB64 = new String(Files.readAllBytes(keyFile.toPath())).trim();
        byte[] wrapped = base64Decode(keyB64);              // 52 bytes
        byte[] nonce = Arrays.copyOfRange(wrapped, 0, 12);
        byte[] ctTag = Arrays.copyOfRange(wrapped, 12, wrapped.length); // ciphertext + 16-byte GCM tag

        Cipher gcm = Cipher.getInstance("AES/GCM/NoPadding");
        gcm.init(Cipher.DECRYPT_MODE, new SecretKeySpec(fieldKey, "AES"), new GCMParameterSpec(128, nonce));
        byte[] plainB64 = gcm.doFinal(ctTag);               // base64 of 16-byte segment key
        byte[] segKey = base64Decode(new String(plainB64, java.nio.charset.StandardCharsets.UTF_8));
        if (segKey.length != 16) throw new IllegalStateException("segment key must be 16 bytes, got " + segKey.length);

        List<File> segs = new ArrayList<>();
        File[] files = epDir.listFiles();
        if (files == null) throw new IllegalStateException("cannot list " + epDir);
        for (File f : files) {
            String n = f.getName();
            if (n.startsWith("seg") && n.endsWith(".ts.enc")) segs.add(f);
        }
        segs.sort(Comparator.comparingInt(f -> Integer.parseInt(f.getName().replaceAll("\\D+", ""))));

        try (FileOutputStream fos = new FileOutputStream(outTs)) {
            Cipher aes = Cipher.getInstance("AES/CBC/PKCS5Padding");
            for (int i = 0; i < segs.size(); i++) {
                byte[] enc = Files.readAllBytes(segs.get(i).toPath());
                aes.init(Cipher.DECRYPT_MODE, new SecretKeySpec(segKey, "AES"), new IvParameterSpec(ivFor(i)));
                byte[] plain = aes.doFinal(enc);
                fos.write(plain);
            }
        }
    }

    static byte[] ivFor(int n) {
        byte[] iv = new byte[16];
        iv[12] = (byte) (n >>> 24);
        iv[13] = (byte) (n >>> 16);
        iv[14] = (byte) (n >>> 8);
        iv[15] = (byte) n;
        return iv;
    }

    static byte[] base64Decode(String s) {
        return Base64.getDecoder().decode(s);
    }
}
