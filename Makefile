.PHONY: clean
# clean development
clean:
	rm -rf build
	rm -rf logs

.PHONY: android
# deploy android
android:
	make clean
	mkdir -p dist
	briefcase create android
	cp -r publish/android/ build/zakat-tracker/android/gradle/app/src/main/res/
	briefcase update android --update-resources
	briefcase build android
	cp build/zakat-tracker/android/gradle/app/build/outputs/apk/debug/app-debug.apk dist/zakat-tracker.apk

.PHONY: macOS
# deploy macOS
macOS:
	make clean
	mkdir -p dist
	briefcase create macos
	briefcase update macos --update-resources
	briefcase build macos
	cp -r build/zakat-tracker/macos/app/متتبع\ الزكاة\ \(Zakat\ Tracker\).app dist/

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