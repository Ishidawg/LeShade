import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami
import org.kde.kirigami.layouts as KL

import "../components"

Kirigami.Page {
    title: "LeShade - Download ReShade"

    ListModel {
        id: releaseModel

        ListElement {
            title: "Crosire slim"
            description: "Default crosire, eg: Deband, UIMask..."
        }
        ListElement {
            title: "Crossire legacy"
            description: "Legacy shaders: eg: AmbientLight..."
        }
        ListElement {
            title: "Sweet FX"
            description: "SMAA, FXAA, CAS..."
        }
    }

    Item {
        anchors.fill: parent
        ColumnLayout {
            //anchors.verticalCenter: parent.verticalCenter
            //anchors.left: parent.left
            //anchors.right: parent.right
            anchors.fill: parent
            spacing: 20

            Controls.Label {
                Layout.maximumWidth: 800
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignJustify
                // topPadding: Kirigami.Units.largeSpacing * 4
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
                        Layout.fillWidth: true
                        model: ListModel {
                            id: versionModel
                            ListElement {
                                text: qsTr("addon")
                            }
                            ListElement {
                                text: qsTr("non-addon")
                            }
                        }
                    }

                    Controls.ComboBox {
                        Layout.fillWidth: true
                        model: downloadBackend.feed_release_version()
                        // model: ListModel {
                        //     id: releaseModel
                        //     ListElement {
                        //         text: qsTr("7.5.1")
                        //     }
                        //     ListElement {
                        //         text: qsTr("7.5.0")
                        //     }
                        // }
                    }
                }

                Controls.Button {
                    Layout.fillWidth: true
                    text: qsTr("Download")

                    onClicked: {
                        downloadBackend.download();
                    }
                }

                Controls.ProgressBar {
                    Layout.fillWidth: true
                    from: 0
                    to: 100
                    value: 0
                    indeterminate: true
                    // value: 50.0
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
