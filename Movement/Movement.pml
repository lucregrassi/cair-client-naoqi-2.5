<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Movement" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="go" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="move" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="learn_place" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="set_position" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="forget_map" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="go_to" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="rest" xar="behavior.xar" />
        <BehaviorDescription name="behavior" src="wakeup" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs />
    <Resources>
        <File name="map" src="map.txt" />
    </Resources>
    <Topics />
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
    </Translations>
</Package>
