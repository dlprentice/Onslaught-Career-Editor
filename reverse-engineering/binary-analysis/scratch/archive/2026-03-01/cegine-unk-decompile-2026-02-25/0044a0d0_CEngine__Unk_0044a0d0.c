/* address: 0x0044a0d0 */
/* name: CEngine__Unk_0044a0d0 */
/* signature: void __thiscall CEngine__Unk_0044a0d0(void * this, int param_1, int param_2) */


void __thiscall CEngine__Unk_0044a0d0(void *this,int param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;

  *(int *)((int)this + 0x4ac) = param_1;
  puVar2 = (undefined4 *)((int)this + (param_1 * 3 + 0x87) * 8);
  puVar3 = (undefined4 *)((int)this + 0x474);
  for (iVar1 = 6; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  D3DDevice__SetViewport((undefined4 *)((int)this + 0x474));
  return;
}
