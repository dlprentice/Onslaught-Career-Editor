/* address: 0x00572fa0 */
/* name: CFastVB__Helper_00572fa0 */
/* signature: int __thiscall CFastVB__Helper_00572fa0(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CFastVB__Helper_00572fa0(void *this,int param_1,void *param_2,void *param_3)

{
  undefined2 *puVar1;
  int iVar2;
  int iVar3;
  void *extraout_EAX;
  uint uVar4;
  undefined2 *puVar5;
  void *pvVar6;
  int iVar7;
  void *pvVar8;

  pvVar6 = *(void **)((int)this + 8);
  iVar2 = *(int *)((int)this + 4);
  iVar7 = param_1 - iVar2 >> 1;
  if (*(int *)((int)this + 0xc) - (int)pvVar6 >> 1 != 0) {
    if ((int)pvVar6 - param_1 >> 1 == 0) {
      CFastVB__Helper_00573140((void *)param_1,pvVar6,(void *)(param_1 + 2));
      MemCopyU16Elements(*(void **)((int)this + 8),
                         1 - ((int)*(void **)((int)this + 8) - param_1 >> 1),param_2);
      puVar5 = *(undefined2 **)((int)this + 8);
      for (; (undefined2 *)param_1 != puVar5; param_1 = param_1 + 2) {
        *(undefined2 *)param_1 = *(undefined2 *)param_2;
      }
    }
    else {
      CFastVB__Helper_00573140((void *)((int)pvVar6 + -2),pvVar6,pvVar6);
      puVar5 = *(undefined2 **)((int)this + 8);
      puVar1 = puVar5;
      while ((undefined2 *)param_1 != puVar1 + -1) {
        puVar5 = puVar5 + -1;
        *puVar5 = puVar1[-2];
        puVar1 = puVar1 + -1;
      }
      puVar5 = (undefined2 *)(param_1 + 2);
      for (; (undefined2 *)param_1 != puVar5; param_1 = param_1 + 2) {
        *(undefined2 *)param_1 = *(undefined2 *)param_2;
      }
    }
    *(int *)((int)this + 8) = *(int *)((int)this + 8) + 2;
    return *(int *)((int)this + 4) + iVar7 * 2;
  }
  if ((iVar2 == 0) || (uVar4 = (int)pvVar6 - iVar2 >> 1, uVar4 < 2)) {
    uVar4 = 1;
  }
  if (iVar2 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = (int)pvVar6 - iVar2 >> 1;
  }
  iVar2 = iVar2 + uVar4;
  iVar3 = iVar2;
  if (iVar2 < 0) {
    iVar3 = 0;
  }
  CFastVB__Helper_00426fd0(iVar3 * 2);
  pvVar8 = extraout_EAX;
  for (pvVar6 = *(void **)((int)this + 4); pvVar6 != (void *)param_1;
      pvVar6 = (void *)((int)pvVar6 + 2)) {
    CFastVB__Helper_00574250(pvVar8,pvVar6);
    pvVar8 = (void *)((int)pvVar8 + 2);
  }
  CFastVB__Helper_00574250(pvVar8,param_2);
  CFastVB__Helper_00573140((void *)param_1,*(void **)((int)this + 8),(void *)((int)pvVar8 + 2));
  VFuncSlot_12_00405db0();
  OID__FreeObject_Callback(*(void **)((int)this + 4));
  *(void **)((int)this + 0xc) = (void *)((int)extraout_EAX + iVar2 * 2);
  iVar2 = CFastVB__CountWordElements((int)this);
  *(void **)((int)this + 4) = extraout_EAX;
  *(int *)((int)this + 8) = (int)extraout_EAX + iVar2 * 2 + 2;
  return (int)(void *)((int)extraout_EAX + iVar7 * 2);
}
