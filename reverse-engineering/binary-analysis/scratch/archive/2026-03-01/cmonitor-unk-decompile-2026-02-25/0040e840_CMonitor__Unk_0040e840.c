/* address: 0x0040e840 */
/* name: CMonitor__Unk_0040e840 */
/* signature: void __fastcall CMonitor__Unk_0040e840(int param_1) */


void __fastcall CMonitor__Unk_0040e840(int param_1)

{
  int iVar1;

  iVar1 = *(int *)(param_1 + 0x528);
  if (iVar1 != 0) {
    *(uint *)(iVar1 + 300) = (uint)(*(int *)(iVar1 + 300) == 0);
  }
  return;
}
