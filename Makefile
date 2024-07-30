.PHONY: clean
# clean development
clean:
	rm -rf build
	rm -rf logs

.PHONY: run
# run application
run:
	briefcase dev -r

.PHONY: update
# update all
update:
	python -m pip install --upgrade briefcase
	python -m pip install --upgrade zakat
	briefcase create
	briefcase update -r

.PHONY: android
# deploy android
android:
	rm -rf build/zakat-tracker/android
	mkdir -p dist
	briefcase create android
	git stash push -m "deploy"
	git checkout main
	cp -r publish/android/ build/zakat-tracker/android/gradle/app/src/main/res/
	cp publish/bundle/android/drawable-xxxhdpi/screen.png build/zakat-tracker/android/gradle/app/src/main/res/mipmap-xxxhdpi/splash.png
	cp publish/bundle/android/drawable-xxhdpi/screen.png build/zakat-tracker/android/gradle/app/src/main/res/mipmap-xxhdpi/splash.png
	cp publish/bundle/android/drawable-xhdpi/screen.png build/zakat-tracker/android/gradle/app/src/main/res/mipmap-xhdpi/splash.png
	cp publish/bundle/android/drawable-mdpi/screen.png build/zakat-tracker/android/gradle/app/src/main/res/mipmap-mdpi/splash.png
	cp publish/bundle/android/drawable-ldpi/screen.png build/zakat-tracker/android/gradle/app/src/main/res/mipmap-ldpi/splash.png
	cp publish/bundle/android/drawable-hdpi/screen.png build/zakat-tracker/android/gradle/app/src/main/res/mipmap-hdpi/splash.png
	briefcase update android --update-resources
	briefcase update android -r
	briefcase build android
	cp build/zakat-tracker/android/gradle/app/build/outputs/apk/debug/app-debug.apk dist/zakat-tracker.apk
	bash version.sh dist/zakat-tracker.apk

.PHONY: macOS
# deploy macOS
macOS:
	rm -rf build/zakat-tracker/macos
	mkdir -p dist
	briefcase create macos
	briefcase update macos --update-resources
	briefcase build macos --update-resources
	cp -r build/zakat-tracker/macos/app/متتبع\ الزكاة\ \(Zakat\ Tracker\).app dist/
	bash version.sh dist/متتبع\ الزكاة\ \(Zakat\ Tracker\).app

# show help
help:
	@echo ''
	@echo 'Usage:'
	@echo ' make [target]'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-0-9]+:/ { \
	helpMessage = match(lastLine, /^# (.*)/); \
			if (helpMessage) { \
					helpCommand = substr($$1, 0, index($$1, ":")-1); \
					helpMessage = substr(lastLine, RSTART + 2, RLENGTH); \
					printf "\033[36m%-22s\033[0m %s\n", helpCommand,helpMessage; \
			} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help