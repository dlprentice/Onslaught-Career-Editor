/* address: 0x00527da0 */
/* name: CVBufTexture__MarkAccepted */
/* signature: void __fastcall CVBufTexture__MarkAccepted(int param_1) */


void __fastcall CVBufTexture__MarkAccepted(int param_1)

{
  if (*(int *)(param_1 + 0x10) == 0) {
    CConsole__Printf(&DAT_0066eb90,s_RM__Accepting___s__d__0064bce4);
  }
  *(undefined4 *)(param_1 + 0x10) = 1;
  return;
}
