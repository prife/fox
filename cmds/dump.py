"%x" %(0xFFFFFFFF+(-328966) +1)

sed -n 's/[ ]*public static final int \(FLAG_[^ ]*\) = \(0[xX][^;]*\);/\2:Intent.\1/p' /Users/prife/Library/Android/sdk/sources/android-25/android/content/Intent.java > intent_flag.txt
