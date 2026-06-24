/* address: 0x004fb280 */
/* name: CUnit__Unk_004fb280 */
/* signature: void __thiscall CUnit__Unk_004fb280(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CUnit__Unk_004fb280(void *this,void *param_1,void *param_2)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  double dVar4;
  float fStack_14;
  int local_10;
  float fStack_c;
  float fStack_8;
  float fStack_4;

  if ((*(int *)((int)this + 0x224) != 0) && ((*(byte *)((int)this + 0x2c) & 4) == 0)) {
    if ((*(int *)((int)this + 0x13c) == 0) ||
       (piVar1 = *(int **)(*(int *)((int)this + 0x13c) + 0xc), piVar1 == (int *)0x0)) {
      if (*(float *)((int)this + 0x20c) < DAT_00672fd0) {
        *(undefined4 *)((int)this + 0xec) = *(undefined4 *)((int)this + 0xf4);
      }
    }
    else {
      if (((*(int *)((int)this + 0x140) != 0) &&
          (iVar2 = *(int *)(*(int *)((int)this + 0x140) + 0xa0), iVar2 != 0)) &&
         (*(int *)(iVar2 + 0x18) != 0)) {
        (**(code **)(*piVar1 + 0x168))(&local_10);
        dVar4 = CEngine__Unk_005094b0
                          (*(void **)((int)this + 0x140),local_10,fStack_c,fStack_8,fStack_4);
        *(float *)((int)this + 0xec) = (float)dVar4;
      }
      *(float *)((int)this + 0x20c) = DAT_00672fd0 + _DAT_005d85cc;
    }
    if (*(float *)((int)this + 0xec) <= _DAT_005d85e8) {
      if (*(float *)((int)this + 0xec) < _DAT_005d85c8) {
        *(undefined4 *)((int)this + 0xec) = 0xbfc90fdb;
      }
    }
    else {
      *(undefined4 *)((int)this + 0xec) = 0x40490fdb;
    }
    uVar3 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar3 = uVar3 & 0x8000ffff;
    if ((int)uVar3 < 0) {
      uVar3 = (uVar3 - 1 | 0xffff0000) + 1;
    }
    fStack_14 = (float)(int)uVar3 * _DAT_005d8c5c + DAT_00672fd0;
    CEventManager__AddEvent_AtTime(&EVENT_MANAGER,0xfa1,this,&fStack_14,0,(void *)0x0,param_1);
  }
  return;
}
