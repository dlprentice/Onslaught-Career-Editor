/* address: 0x004b8800 */
/* name: CUnitAI__Unk_004b8800 */
/* signature: void __fastcall CUnitAI__Unk_004b8800(int param_1) */


void __fastcall CUnitAI__Unk_004b8800(int param_1)

{
  int unaff_retaddr;

  if (DAT_00662f44 == 0) {
    if (*(char *)(param_1 + 0x1c0) != '\0') {
      *(undefined1 *)(param_1 + 0x1c0) = 0;
    }
    if (DAT_008073d0 != (undefined4 *)0x0) {
      CMessageBox__Helper_004e1200(&DAT_00896988,(int)DAT_008073d0,unaff_retaddr);
      if (DAT_008073d0 != (undefined4 *)0x0) {
        (**(code **)*DAT_008073d0)(1);
        DAT_008073d0 = (undefined4 *)0x0;
      }
    }
  }
  return;
}
