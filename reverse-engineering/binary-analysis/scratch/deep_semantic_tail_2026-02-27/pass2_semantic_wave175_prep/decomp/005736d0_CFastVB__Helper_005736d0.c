/* address: 0x005736d0 */
/* name: CFastVB__Helper_005736d0 */
/* signature: void __thiscall CFastVB__Helper_005736d0(void * this, int param_1, void * param_2, uint param_3, void * param_4) */


void __thiscall
CFastVB__Helper_005736d0(void *this,int param_1,void *param_2,uint param_3,void *param_4)

{
  int iVar1;
  int iVar2;
  undefined4 *extraout_EAX;
  undefined4 *puVar3;
  void *pvVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;

  puVar6 = *(undefined4 **)((int)this + 8);
  if (param_2 <= (void *)(*(int *)((int)this + 0xc) - (int)puVar6 >> 2)) {
    if ((void *)((int)puVar6 - param_1 >> 2) < param_2) {
      puVar3 = (undefined4 *)((int)param_2 * 4 + param_1);
      if ((undefined4 *)param_1 != puVar6) {
        puVar5 = puVar3 + -(int)param_2;
        do {
          if (puVar3 != (undefined4 *)0x0) {
            *puVar3 = *puVar5;
          }
          puVar5 = puVar5 + 1;
          puVar3 = puVar3 + 1;
        } while (puVar5 != puVar6);
      }
      puVar6 = *(undefined4 **)((int)this + 8);
      for (iVar1 = (int)param_2 - ((int)puVar6 - param_1 >> 2); iVar1 != 0; iVar1 = iVar1 + -1) {
        if (puVar6 != (undefined4 *)0x0) {
          *puVar6 = *(undefined4 *)param_3;
        }
        puVar6 = puVar6 + 1;
      }
      puVar6 = *(undefined4 **)((int)this + 8);
      for (; (undefined4 *)param_1 != puVar6; param_1 = param_1 + 4) {
        *(undefined4 *)param_1 = *(undefined4 *)param_3;
      }
      *(int *)((int)this + 8) = *(int *)((int)this + 8) + (int)param_2 * 4;
      return;
    }
    if (param_2 != (void *)0x0) {
      puVar3 = puVar6;
      for (puVar5 = puVar6 + -(int)param_2; puVar5 != puVar6; puVar5 = puVar5 + 1) {
        if (puVar3 != (undefined4 *)0x0) {
          *puVar3 = *puVar5;
        }
        puVar3 = puVar3 + 1;
      }
      puVar6 = *(undefined4 **)((int)this + 8);
      for (puVar3 = puVar6 + -(int)param_2; (undefined4 *)param_1 != puVar3; puVar3 = puVar3 + -1) {
        puVar6 = puVar6 + -1;
        *puVar6 = puVar3[-1];
      }
      puVar6 = (undefined4 *)(param_1 + (int)param_2 * 4);
      for (; (undefined4 *)param_1 != puVar6; param_1 = param_1 + 4) {
        *(undefined4 *)param_1 = *(undefined4 *)param_3;
      }
      *(int *)((int)this + 8) = *(int *)((int)this + 8) + (int)param_2 * 4;
    }
    return;
  }
  iVar1 = *(int *)((int)this + 4);
  if ((iVar1 == 0) || (pvVar4 = (void *)((int)puVar6 - iVar1 >> 2), pvVar4 <= param_2)) {
    pvVar4 = param_2;
  }
  if (iVar1 == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = (int)puVar6 - iVar1 >> 2;
  }
  iVar1 = iVar1 + (int)pvVar4;
  iVar2 = iVar1;
  if (iVar1 < 0) {
    iVar2 = 0;
  }
  CFastVB__Helper_00426fd0(iVar2 * 4);
  puVar3 = extraout_EAX;
  for (puVar6 = *(undefined4 **)((int)this + 4); pvVar4 = param_2, puVar5 = puVar3,
      puVar6 != (undefined4 *)param_1; puVar6 = puVar6 + 1) {
    if (puVar3 != (undefined4 *)0x0) {
      *puVar3 = *puVar6;
    }
    puVar3 = puVar3 + 1;
  }
  for (; pvVar4 != (void *)0x0; pvVar4 = (void *)((int)pvVar4 + -1)) {
    if (puVar5 != (undefined4 *)0x0) {
      *puVar5 = *(undefined4 *)param_3;
    }
    puVar5 = puVar5 + 1;
  }
  puVar5 = *(undefined4 **)((int)this + 8);
  puVar6 = puVar3 + (int)param_2;
  if ((undefined4 *)param_1 != puVar5) {
    puVar3 = (undefined4 *)((int)puVar6 + param_1 + ((int)param_2 * -4 - (int)puVar3));
    do {
      if (puVar6 != (undefined4 *)0x0) {
        *puVar6 = *puVar3;
      }
      puVar3 = puVar3 + 1;
      puVar6 = puVar6 + 1;
    } while (puVar3 != puVar5);
  }
  OID__FreeObject_Callback(*(void **)((int)this + 4));
  *(undefined4 **)((int)this + 0xc) = extraout_EAX + iVar1;
  iVar1 = *(int *)((int)this + 4);
  if (iVar1 == 0) {
    *(undefined4 **)((int)this + 4) = extraout_EAX;
    *(undefined4 **)((int)this + 8) = extraout_EAX + (int)param_2;
    return;
  }
  *(undefined4 **)((int)this + 4) = extraout_EAX;
  *(undefined4 **)((int)this + 8) =
       extraout_EAX + (*(int *)((int)this + 8) - iVar1 >> 2) + (int)param_2;
  return;
}
