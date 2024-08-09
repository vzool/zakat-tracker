#!/bin/bash

if [ -f publish/android/debug.keystore ] ; then
    echo "debug.keystore already exists, skipping creation."
else
    echo "Creating debug.keystore..."
    keytool -genkeypair -alias android-debug-key -keyalg RSA -keysize 4096 -validity 2739931 -keystore publish/android/debug.keystore -storepass "zakat-tracker" -keypass "zakat-tracker" -dname "CN=Abdelaziz Elrashed Elshaikh Mohamed, OU=IT, O=Zakat Movement, L=Omdurman, S=Khartoum, C=SD"
fi
