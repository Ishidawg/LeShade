import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami
import org.kde.kirigami.layouts as KL

import "../components"

Kirigami.Page {
    title: qsTr("LeShade - Clone")

    ListModel {
        id: cloneModel

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

    Component {
        id: cloneDelegate
        CloneScroll {}
    }

    Item {
        anchors.fill: parent

        ColumnLayout {
            // Fills horizontally only
            anchors.fill: parent
            spacing: 20

            Controls.Label {
                Layout.alignment: Qt.AlignHCenter
                Layout.maximumWidth: 800
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignJustify
                text: qsTr("Scroll down through the shader repositories and select those you want to install.")
            }

            ColumnLayout {
                Layout.alignment: Qt.AlignHCenter
                Layout.maximumWidth: 800
                Layout.fillHeight: true
                spacing: 12

                Kirigami.CardsListView {
                    id: cloneCards
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    // Contains info to be displayed
                    model: cloneModel
                    // Delegate hows the info will be presented in the ListView
                    delegate: cloneDelegate

                    // Controls.ScrollBar.vertical: Controls.ScrollBar {
                    //     policy: Controls.ScrollBar.AlwaysOn
                    // }
                }

                Controls.Button {
                    Layout.fillWidth: true
                    text: qsTr("Install")
                }

                Controls.ProgressBar {
                    Layout.fillWidth: true
                    from: 0
                    to: 100
                    indeterminate: true
                }
            }

            Item {
                Layout.fillHeight: true
            }

            ActionButtons {
                Layout.alignment: Qt.AlignHCenter

                nextButton.text: qsTr("Close")

                onBackClicked: {
                    KL.PageStack.replace(Qt.resolvedUrl("InstallPage.qml"));
                }
                onNextClicked: {
                    Qt.quit();
                }
            }
        }
    }
}
