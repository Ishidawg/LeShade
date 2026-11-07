import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.Page {
	title: qsTr("LeShade - A ReShade Manager")

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
				wrapMode: Text.WordWrap
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
					text: qsTr("Install")
				}
				Controls.Button {
					Layout.alignment: Qt.AlignTop
					text: qsTr("Uninstall")
				}
			}
		}
	}
}
