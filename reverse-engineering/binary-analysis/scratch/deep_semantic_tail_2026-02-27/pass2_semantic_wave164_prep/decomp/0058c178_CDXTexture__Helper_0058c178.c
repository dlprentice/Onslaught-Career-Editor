/* address: 0x0058c178 */
/* name: CDXTexture__Helper_0058c178 */
/* signature: int __thiscall CDXTexture__Helper_0058c178(void * this, int param_1, uint param_2, void * param_3) */


int __thiscall CDXTexture__Helper_0058c178(void *this,int param_1,uint param_2,void *param_3)

{
  uint uVar1;
  uint uVar2;
  undefined4 *extraout_EAX;
  undefined4 *extraout_EAX_00;
  uint uVar3;
  uint uVar4;
  int iVar5;
  undefined4 *puVar6;
  uint uVar7;
  undefined4 *puVar8;
  int local_10;
  uint local_8;

  uVar1 = *(uint *)((int)this + 0x14);
  uVar7 = 0;
  local_8 = uVar1 >> 1;
  local_10 = 0;
  uVar3 = uVar1;
  if (uVar1 == 0) {
LAB_0058c1c0:
    if (uVar1 == (~uVar1 + 1 & uVar1)) {
      if (uVar1 == 0) {
        iVar5 = 1;
      }
      else {
        iVar5 = uVar1 * 2;
      }
      CFastVB__Helper_00426fd0(iVar5 << 2);
      if (extraout_EAX != (undefined4 *)0x0) {
        puVar6 = *(undefined4 **)((int)this + 0x1c);
        puVar8 = extraout_EAX;
        for (uVar7 = *(uint *)((int)this + 0x14) & 0x3fffffff; uVar7 != 0; uVar7 = uVar7 - 1) {
          *puVar8 = *puVar6;
          puVar6 = puVar6 + 1;
          puVar8 = puVar8 + 1;
        }
        for (iVar5 = 0; iVar5 != 0; iVar5 = iVar5 + -1) {
          *(undefined1 *)puVar8 = *(undefined1 *)puVar6;
          puVar6 = (undefined4 *)((int)puVar6 + 1);
          puVar8 = (undefined4 *)((int)puVar8 + 1);
        }
        OID__FreeObject_Callback(*(void **)((int)this + 0x1c));
        *(undefined4 **)((int)this + 0x1c) = extraout_EAX;
        if (*(int *)((int)this + 0x14) == 0) {
          iVar5 = 1;
        }
        else {
          iVar5 = *(int *)((int)this + 0x14) * 2;
        }
        CFastVB__Helper_00426fd0(iVar5 << 2);
        if (extraout_EAX_00 != (undefined4 *)0x0) {
          puVar6 = *(undefined4 **)((int)this + 0x18);
          puVar8 = extraout_EAX_00;
          for (uVar7 = *(uint *)((int)this + 0x14) & 0x3fffffff; uVar7 != 0; uVar7 = uVar7 - 1) {
            *puVar8 = *puVar6;
            puVar6 = puVar6 + 1;
            puVar8 = puVar8 + 1;
          }
          for (iVar5 = 0; iVar5 != 0; iVar5 = iVar5 + -1) {
            *(undefined1 *)puVar8 = *(undefined1 *)puVar6;
            puVar6 = (undefined4 *)((int)puVar6 + 1);
            puVar8 = (undefined4 *)((int)puVar8 + 1);
          }
          OID__FreeObject_Callback(*(void **)((int)this + 0x18));
          *(undefined4 **)((int)this + 0x18) = extraout_EAX_00;
          goto LAB_0058c26b;
        }
      }
      local_10 = -0x7ff8fff2;
      goto LAB_0058c2a7;
    }
LAB_0058c26b:
    for (uVar7 = *(uint *)((int)this + 0x14); local_8 < uVar7; uVar7 = uVar7 - 1) {
      puVar6 = (undefined4 *)(*(int *)((int)this + 0x18) + uVar7 * 4);
      *puVar6 = puVar6[-1];
      puVar6 = (undefined4 *)(*(int *)((int)this + 0x1c) + uVar7 * 4);
      *puVar6 = puVar6[-1];
    }
    *(int *)(*(int *)((int)this + 0x18) + local_8 * 4) = param_1;
    *(undefined4 *)(*(int *)((int)this + 0x1c) + local_8 * 4) = 1;
    *(int *)((int)this + 0x14) = *(int *)((int)this + 0x14) + 1;
  }
  else {
    do {
      uVar2 = *(uint *)(*(int *)((int)this + 0x18) + local_8 * 4);
      if (uVar2 < (uint)param_1) {
        uVar7 = local_8 + 1;
        uVar4 = uVar3;
      }
      else {
        uVar4 = local_8;
        if (uVar2 <= (uint)param_1) break;
      }
      local_8 = uVar4 + uVar7 >> 1;
      uVar3 = uVar4;
    } while (uVar7 < uVar4);
    if (uVar3 <= uVar7) goto LAB_0058c1c0;
  }
  if (param_2 != 0) {
    *(uint *)param_2 = local_8;
  }
LAB_0058c2a7:
  OID__FreeObject_Callback((void *)0x0);
  return local_10;
}
