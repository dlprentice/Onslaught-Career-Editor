/* address: 0x0047cea0 */
/* name: CUnitAI__ClearLinkedThingFlagsAndResetCounter */
/* signature: void __fastcall CUnitAI__ClearLinkedThingFlagsAndResetCounter(int param_1) */


void __fastcall CUnitAI__ClearLinkedThingFlagsAndResetCounter(int param_1)

{
  undefined4 *puVar1;
  void *this;
  int unaff_ESI;

  puVar1 = *(undefined4 **)(param_1 + 0x1d4);
  if (puVar1 == (undefined4 *)0x0) {
    this = (void *)0x0;
  }
  else {
    this = (void *)*puVar1;
  }
  while (this != (void *)0x0) {
    CUnit__Helper_004cb0b0(this,0,unaff_ESI);
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      this = (void *)0x0;
    }
    else {
      this = (void *)*puVar1;
    }
  }
  *(undefined4 *)(param_1 + 0x1e4) = 0;
  return;
}
