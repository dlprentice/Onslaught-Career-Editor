/* address: 0x00512630 */
/* name: Platform__HandleDeviceLostAndRestore */
/* signature: void __fastcall Platform__HandleDeviceLostAndRestore(int param_1) */


void __fastcall Platform__HandleDeviceLostAndRestore(int param_1)

{
  int iVar1;

  iVar1 = (**(code **)(**(int **)(param_1 + 0x32ea0) + 0x44))(*(int **)(param_1 + 0x32ea0),0,0,0,0);
  if (iVar1 == -0x7789f798) {
    while (iVar1 = (**(code **)(*DAT_00888a50 + 0xc))(DAT_00888a50), iVar1 < 0) {
      Sleep(100);
    }
    DAT_0082b5b0 = 1;
  }
  return;
}
