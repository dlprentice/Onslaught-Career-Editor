/* address: 0x00573170 */
/* name: CFastVB__InsertDwordAndGrow */
/* signature: int __thiscall CFastVB__InsertDwordAndGrow(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CFastVB__InsertDwordAndGrow(void *this,int param_1,void *param_2,void *param_3)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  void *extraout_EAX;
  uint uVar4;
  undefined4 *puVar5;
  void *pvVar6;
  int iVar7;
  void *pvVar8;

  pvVar6 = *(void **)((int)this + 8);
  iVar2 = *(int *)((int)this + 4);
  iVar7 = param_1 - iVar2 >> 2;
  if (*(int *)((int)this + 0xc) - (int)pvVar6 >> 2 != 0) {
    if ((int)pvVar6 - param_1 >> 2 == 0) {
      CFastVB__CopyDwordRange((void *)param_1,pvVar6,(void *)(param_1 + 4));
      CTexture__Helper_00573ff0
                (*(void **)((int)this + 8),1 - ((int)*(void **)((int)this + 8) - param_1 >> 2),
                 param_2);
      puVar5 = *(undefined4 **)((int)this + 8);
      for (; (undefined4 *)param_1 != puVar5; param_1 = param_1 + 4) {
        *(undefined4 *)param_1 = *(undefined4 *)param_2;
      }
    }
    else {
      CFastVB__CopyDwordRange((void *)((int)pvVar6 + -4),pvVar6,pvVar6);
      puVar5 = *(undefined4 **)((int)this + 8);
      puVar1 = puVar5;
      while ((undefined4 *)param_1 != puVar1 + -1) {
        puVar5 = puVar5 + -1;
        *puVar5 = puVar1[-2];
        puVar1 = puVar1 + -1;
      }
      puVar5 = (undefined4 *)(param_1 + 4);
      for (; (undefined4 *)param_1 != puVar5; param_1 = param_1 + 4) {
        *(undefined4 *)param_1 = *(undefined4 *)param_2;
      }
    }
    *(int *)((int)this + 8) = *(int *)((int)this + 8) + 4;
    return *(int *)((int)this + 4) + iVar7 * 4;
  }
  if ((iVar2 == 0) || (uVar4 = (int)pvVar6 - iVar2 >> 2, uVar4 < 2)) {
    uVar4 = 1;
  }
  if (iVar2 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = (int)pvVar6 - iVar2 >> 2;
  }
  iVar2 = iVar2 + uVar4;
  iVar3 = iVar2;
  if (iVar2 < 0) {
    iVar3 = 0;
  }
  CFastVB__Helper_00426fd0(iVar3 * 4);
  pvVar8 = extraout_EAX;
  for (pvVar6 = *(void **)((int)this + 4); pvVar6 != (void *)param_1;
      pvVar6 = (void *)((int)pvVar6 + 4)) {
    CFastVB__AssignDwordIfDestNotNull(pvVar8,pvVar6);
    pvVar8 = (void *)((int)pvVar8 + 4);
  }
  CFastVB__AssignDwordIfDestNotNull(pvVar8,param_2);
  CFastVB__CopyDwordRange((void *)param_1,*(void **)((int)this + 8),(void *)((int)pvVar8 + 4));
  VFuncSlot_12_00405db0();
  OID__FreeObject_Callback(*(void **)((int)this + 4));
  *(void **)((int)this + 0xc) = (void *)((int)extraout_EAX + iVar2 * 4);
  iVar2 = CFastVB__CountDwordsFromPointerSpan((int)this);
  *(void **)((int)this + 4) = extraout_EAX;
  *(int *)((int)this + 8) = (int)extraout_EAX + iVar2 * 4 + 4;
  return (int)(void *)((int)extraout_EAX + iVar7 * 4);
}
