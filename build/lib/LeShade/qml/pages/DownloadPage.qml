import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami
import org.kde.kirigami.layouts as KL

import "../components"

Kirigami.Page {
    title: "LeShade - Download ReShade"
    property var releaseVersions: []

    // Listen to signal from DownloadBackend (Download.py)
    Connections {
        target: downloadBackend

        function onRelease_version_ready(versions) {
            releaseVersions = versions;

            if (releaseVersions.length > 0) {
                releaseSelector.currentIndex = 0;
                downloadBackend.get_release(releaseSelector.currentText);
            }
        }

        function onRelease_version_failed(message) {
            console.error("Failed to get ReShade tags:", message);
        }

        function onReshade_download_finished(value) {
            if (value) {
                console.log("Signal: ", value);
                progressbar.indeterminate = false;
                progressbar.value = 100;
                return;
            }
        }

        function onReshade_download_failed(message) {
            console.error("Failed to download ReShade", message);
        }
    }

    Item {
        anchors.fill: parent
        ColumnLayout {
            anchors.fill: parent
            spacing: 20

            Controls.Label {
                Layout.maximumWidth: 800
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignJustify
                bottomPadding: Kirigami.Units.largeSpacing * 2
                text: qsTr("Here you choose what version of ReShade you want to install: Addon or non-addon support. Select the ReShade release version too (nightly to have the latest one). Keep in mind that is recommended to not use addon support for multiplayer games with anti-cheat.")
            }

            ColumnLayout {
                Layout.alignment: Qt.AlignHCenter
                Layout.maximumWidth: 800
                Layout.fillHeight: true
                spacing: 12

                RowLayout {
                    Layout.fillWidth: true

                    Controls.ComboBox {
                        id: versionSelector
                        Layout.fillWidth: true
                        model: ListModel {
                            id: versionModel
                            ListElement {
                                text: qsTr("Addon")
                            }
                            ListElement {
                                text: qsTr("Non-Addon")
                            }
                        }
                        onActivated: {
                            downloadBackend.get_version(currentText);
                        }
                    }

                    Controls.ComboBox {
                        id: releaseSelector
                        Layout.fillWidth: true
                        model: releaseVersions
                        Component.onCompleted: {
                            downloadBackend.feed_release_version();
                        }
                        onActivated: {
                            downloadBackend.get_release(currentText);
                        }
                        // Component.onCompleted: {
                        //     downloadBackend.getRelease(currentText);
                        // }
                        // onActivated: {
                        //     downloadBackend.getRelease(currentText);
                        // }
                    }
                }

                Controls.Button {
                    Layout.fillWidth: true
                    text: qsTr("Download")

                    onClicked: {
                        progressbar.indeterminate = true;
                        downloadBackend.download();
                    }
                }

                Controls.ProgressBar {
                    id: progressbar
                    Layout.fillWidth: true
                    from: 0
                    to: 100
                    value: 0
                    indeterminate: false
                }
            }

            Item {
                Layout.fillHeight: true
            }

            ActionButtons {
                Layout.alignment: Qt.AlignHCenter
                onBackClicked: {
                    KL.PageStack.replace(Qt.resolvedUrl("HomePage.qml"));
                }
                onNextClicked: {
                    KL.PageStack.replace(Qt.resolvedUrl("InstallPage.qml"));
                }
            }
        }
    }
}
