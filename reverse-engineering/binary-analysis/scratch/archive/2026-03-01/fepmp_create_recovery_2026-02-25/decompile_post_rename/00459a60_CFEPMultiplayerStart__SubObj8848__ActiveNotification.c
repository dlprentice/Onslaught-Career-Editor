/* address: 0x00459a60 */
/* name: CFEPMultiplayerStart__SubObj8848__ActiveNotification */
/* signature: undefined CFEPMultiplayerStart__SubObj8848__ActiveNotification(void) */


void __thiscall CFEPMultiplayerStart__SubObj8848__ActiveNotification(int param_1,int param_2)

{
  if ((param_2 == 5) || (param_2 == 6)) {
    *(undefined4 *)
     (param_1 + 0x57c + (*(int *)(param_1 + 0x346c) + *(int *)(param_1 + 0x3468) * 6) * 4) =
         0x3f800000;
  }
  *(undefined4 *)(param_1 + 0x347c) = 0;
  return;
}
