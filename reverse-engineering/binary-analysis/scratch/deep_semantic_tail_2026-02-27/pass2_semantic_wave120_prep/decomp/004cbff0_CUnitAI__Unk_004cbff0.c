/* address: 0x004cbff0 */
/* name: CUnitAI__Unk_004cbff0 */
/* signature: void __fastcall CUnitAI__Unk_004cbff0(void * param_1) */


void __fastcall CUnitAI__Unk_004cbff0(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;

  iVar1 = *(int *)param_1;
  while (iVar1 != 0) {
    puVar2 = *(undefined4 **)param_1;
    iVar1 = puVar2[0xe];
    if (puVar2 != (undefined4 *)0x0) {
      (**(code **)*puVar2)(1);
    }
    *(int *)param_1 = iVar1;
  }
  return;
}
