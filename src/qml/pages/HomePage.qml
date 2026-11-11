import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.Page {
  title: qsTr("LeShade - A ReShade Manager")

	// Component {
	// 	id: uninstallPageComponent
	// 	UninstallPage {}
	// }

	Item {
		// Container that fills the parent window, so, parent = ruler
		anchors.fill: parent

		ColumnLayout {
			// Fills horizontally only
			anchors.left: parent.left
			anchors.right: parent.right
			anchors.verticalCenter: parent.verticalCenter

			Image {
				Layout.alignment: Qt.AlignHCenter
				sourceSize.width: 142
        sourceSize.height: 142
				fillMode: Image.PreserveAspectFit
				source: "../../assets/logo.png"
			}

			Controls.Label {
				Layout.fillWidth: true
				Layout.maximumWidth: 800
				Layout.alignment: Qt.AlignHCenter

				wrapMode: Text.WordWrap
				horizontalAlignment: Text.AlignJustify

				leftPadding: Kirigami.Units.largeSpacing * 10
				rightPadding: Kirigami.Units.largeSpacing * 10
				topPadding: Kirigami.Units.largeSpacing * 4
				bottomPadding: Kirigami.Units.largeSpacing * 2

				text: qsTr("LeShade is a manager for ReShade installations on Linux. It's a native tool that can manage multiple ReShade versions across many games that use Proton or Wine.")
			}
			RowLayout {
				Layout.alignment: Qt.AlignHCenter

				Controls.Button {
					Layout.alignment: Qt.AlignTop
					icon.name: "list-add-symbolic"
					text: qsTr("Install")

					Controls.ToolTip.delay: 1000
					Controls.ToolTip.timeout: 5000
					Controls.ToolTip.visible: hovered
					Controls.ToolTip.text: qsTr("Install Reshade on a Game")
				}
				Controls.Button {
					Layout.alignment: Qt.AlignTop
					icon.name: "user-trash-symbolic"
					text: qsTr("Uninstall")

					Controls.ToolTip.delay: 1000
					Controls.ToolTip.timeout: 5000
					Controls.ToolTip.visible: hovered
					Controls.ToolTip.text: qsTr("Open uninstall page")

          onClicked: {
					  // applicationWindow().pageStack.replace(uninstallPageComponent)
            applicationWindow().pageStack.replace(
              Qt.resolvedUrl("UninstallPage.qml")
            )
					}
				}
			}
		}
	}
}
