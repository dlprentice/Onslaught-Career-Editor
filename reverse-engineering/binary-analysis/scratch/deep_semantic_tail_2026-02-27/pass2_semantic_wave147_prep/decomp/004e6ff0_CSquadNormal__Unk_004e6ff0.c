/* address: 0x004e6ff0 */
/* name: CSquadNormal__Unk_004e6ff0 */
/* signature: void __thiscall CSquadNormal__Unk_004e6ff0(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CSquadNormal__Unk_004e6ff0(void *this,int param_1,void *param_2)

{
  int iVar1;
  float10 fVar2;

  if (param_1 != 0) {
    fVar2 = (float10)(**(code **)(*(int *)param_1 + 0x44))();
    *(float *)((int)this + 0x104) = (float)fVar2;
    iVar1 = CUnit__GetGridMapByType(param_1);
    *(int *)((int)this + 0xd0) = iVar1;
    fVar2 = (float10)(**(code **)(*(int *)param_1 + 0x1bc))();
    *(float *)((int)this + 0x10c) = (float)(fVar2 * (float10)_DAT_005df254);
    *(undefined4 *)((int)this + 0xc0) = *(undefined4 *)(param_1 + 0x34);
  }
  return;
}
