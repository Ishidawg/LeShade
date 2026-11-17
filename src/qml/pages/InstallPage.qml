import QtQuick
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "../components"

Kirigami.Page {
    title: "LeShade - Install Files"

    FileDialog {
        id: fileDialog
        title: qsTr("Select Game Executable")
        fileMode: FileDialog.OpenFile
        nameFilters: ["Executable files (*.exe)"]
        onAccepted: {
            filePathField.text = fileDialog.selectedFile;
        }
    }

    Item {
        anchors.fill: parent

        ColumnLayout {
            anchors.fill: parent
            // Layout.alignment: Qt.AlignHCenter
            spacing: 20

            ColumnLayout {
                Layout.alignment: Qt.AlignHCenter
                Layout.maximumWidth: 800
                Layout.fillHeight: true
                spacing: 12

                Controls.Label {
                    Layout.alignment: Qt.AlignHCenter
                    Layout.maximumWidth: 800
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignJustify
                    topPadding: Kirigami.Units.largeSpacing * 4
                    text: qsTr("Select the game executable:")
                }

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    Layout.maximumWidth: 800
                    Layout.fillWidth: true
                    spacing: 8

                    Controls.TextField {
                        id: filePathField
                        placeholderText: qsTr("mygame/game.exe")
                        Layout.fillWidth: true
                        selectByMouse: true
                    }

                    Controls.Button {
                        text: qsTr("Browse")
                        onClicked: fileDialog.open()
                    }
                }

                GridLayout {
                    Layout.alignment: Qt.AlignHCenter
                    Layout.maximumWidth: 800
                    Layout.fillWidth: true
                    Layout.topMargin: 20
                    Layout.bottomMargin: 20
                    columns: 3
                    rowSpacing: Kirigami.Units.largeSpacing
                    columnSpacing: Kirigami.Units.largeSpacing

                    Controls.RadioButton {
                        checked: false
                        text: qsTr("OpenGL")
                    }

                    Controls.RadioButton {
                        checked: false
                        text: qsTr("D3D 8")
                    }

                    Controls.RadioButton {
                        checked: false
                        text: qsTr("D3D 9")
                    }

                    Controls.RadioButton {
                        checked: true
                        text: qsTr("D3D 10/11/12")
                    }

                    Controls.RadioButton {
                        checked: false
                        text: qsTr("Vulkan")
                    }
                }

                Controls.Button {
                    Layout.fillWidth: true
                    text: qsTr("Install")
                }

                Controls.ProgressBar {
                    Layout.fillWidth: true
                    value: 50.0
                }
            }

            Item {
                Layout.fillHeight: true
            }

            ActionButtons {
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }
}
