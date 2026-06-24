/* address: 0x0053d3a0 */
/* name: CLTShell__Helper_0053d3a0 */
/* signature: void __fastcall CLTShell__Helper_0053d3a0(int param_1) */


void __fastcall CLTShell__Helper_0053d3a0(int param_1)

{
  int iVar1;

  if (*(int *)(param_1 + 0x4e4) != 0) {
    CHud__Helper_004f27e0(*(int *)(param_1 + 0x4e4) + 8);
    *(undefined4 *)(param_1 + 0x4e4) = 0;
  }
  iVar1 = *(int *)(param_1 + 0x28);
  if (iVar1 != 0) {
    *(int *)(iVar1 + 0x170) = *(int *)(iVar1 + 0x170) + -1;
    *(undefined4 *)(param_1 + 0x28) = 0;
  }
  return;
}
