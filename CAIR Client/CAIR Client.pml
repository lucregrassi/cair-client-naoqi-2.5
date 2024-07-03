<?xml version="1.0" encoding="UTF-8" ?>
<Package name="CAIR Client" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="cair_client" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs />
    <Resources>
        <File name="DialogueMode" src="html/img/DialogueMode.png" />
        <File name="ExecutionMode" src="html/img/ExecutionMode.png" />
        <File name="PrivacyMode" src="html/img/PrivacyMode.png" />
        <File name="gzip" src="libs/gzip.py" />
        <File name="nuance_vectors" src="nuance_vectors.json" />
        <File name="RICE" src="html/img/RICE.png" />
        <File name="CAIRclient_SoftBank_actions" src="libs/cair_libraries/client_softbank_action_manager.py" />
        <File name="CAIRclient_SoftBank_utils" src="libs/cair_libraries/client_softbank_utils.py" />
        <File name="CAIRclient_alterego_utils" src="libs/cair_libraries/client_alterego_utils.py" />
        <File name="CAIRclient_utils" src="libs/cair_libraries/client_utils.py" />
        <File name="DialogueNuances" src="libs/cair_libraries/dialogue_nuances.py" />
        <File name="DialogueSentencePiece" src="libs/cair_libraries/dialogue_sentence_piece.py" />
        <File name="DialogueState" src="libs/cair_libraries/dialogue_state.py" />
        <File name="DialogueStatistics" src="libs/cair_libraries/dialogue_statistics.py" />
        <File name="DialogueTurn" src="libs/cair_libraries/dialogue_turn.py" />
        <File name="SpeakerInfo" src="libs/cair_libraries/speaker_info.py" />
        <File name="Utils" src="libs/cair_libraries/server_utils.py" />
        <File name="__init__" src="libs/cair_libraries/__init__.py" />
        <File name="" src="libs/cair_libraries/.gitignore" />
        <File name="trigger_sentences_cn-CN" src="trigger_sentences/trigger_sentences_cn-CN.txt" />
        <File name="trigger_sentences_en-US" src="trigger_sentences/trigger_sentences_en-US.txt" />
        <File name="trigger_sentences_es-ES" src="trigger_sentences/trigger_sentences_es-ES.txt" />
        <File name="trigger_sentences_fr-FR" src="trigger_sentences/trigger_sentences_fr-FR.txt" />
        <File name="trigger_sentences_it-IT" src="trigger_sentences/trigger_sentences_it-IT.txt" />
        <File name="QR_code" src="html/img/QR_code.png" />
        <File name="client_softbank_personalization_server" src="libs/cair_libraries/client_softbank_personalization_server.py" />
    </Resources>
    <Topics />
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
        <Translation name="translation_it_IT" src="translations/translation_it_IT.ts" language="it_IT" />
    </Translations>
</Package>
