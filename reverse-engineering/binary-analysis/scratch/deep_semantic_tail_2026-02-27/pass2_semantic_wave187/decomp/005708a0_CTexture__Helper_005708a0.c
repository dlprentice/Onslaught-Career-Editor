/* address: 0x005708a0 */
/* name: CTexture__Helper_005708a0 */
/* signature: void __thiscall CTexture__Helper_005708a0(void * this, int param_1, int param_2, int param_3) */


/* WARNING: Removing unreachable block (ram,0x00570a33) */
/* WARNING: Removing unreachable block (ram,0x00570a48) */
/* WARNING: Removing unreachable block (ram,0x00570a57) */
/* WARNING: Removing unreachable block (ram,0x00570a60) */

void __thiscall CTexture__Helper_005708a0(void *this,int param_1,int param_2,int param_3)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  void *extraout_EAX;
  void *extraout_EAX_00;
  undefined4 *puVar5;
  uint uVar6;
  void *unaff_EDI;
  int local_c;

  if (*(int *)(param_2 + 4) == 0) {
    iVar3 = 0;
  }
  else {
    iVar3 = *(int *)(param_2 + 8) - *(int *)(param_2 + 4) >> 2;
  }
  iVar3 = iVar3 + -1;
  if (-1 < iVar3) {
    do {
      CFastVB__InsertDwordSpanFilled
                ((void *)((int)this + 0xc),*(int *)((int)this + 0x14),(void *)0x1,
                 *(int *)(param_2 + 4) + iVar3 * 4,unaff_EDI);
      iVar3 = iVar3 + -1;
    } while (-1 < iVar3);
  }
  if (*(int *)(param_1 + 4) == 0) {
    param_2 = 0;
  }
  else {
    param_2 = *(int *)(param_1 + 8) - *(int *)(param_1 + 4) >> 2;
  }
  local_c = 0;
  if (0 < param_2) {
    do {
      puVar1 = (undefined4 *)(*(int *)(param_1 + 4) + local_c * 4);
      puVar5 = *(undefined4 **)((int)this + 0x14);
      if (*(int *)((int)this + 0x18) - (int)puVar5 >> 2 == 0) {
        iVar3 = *(int *)((int)this + 0x10);
        if ((iVar3 == 0) || (uVar6 = (int)puVar5 - iVar3 >> 2, uVar6 < 2)) {
          uVar6 = 1;
        }
        if (iVar3 == 0) {
          iVar3 = 0;
        }
        else {
          iVar3 = (int)puVar5 - iVar3 >> 2;
        }
        iVar3 = iVar3 + uVar6;
        iVar4 = iVar3;
        if (iVar3 < 0) {
          iVar4 = 0;
        }
        OID__AllocObject_DefaultTag_00662b2c(iVar4 * 4);
        CFastVB__CopyDwordRange(*(void **)((int)this + 0x10),puVar5,extraout_EAX);
        CTexture__Helper_00573ff0(extraout_EAX_00,1,puVar1);
        CFastVB__CopyDwordRange
                  (puVar5,*(void **)((int)this + 0x14),(void *)((int)extraout_EAX_00 + 4));
        VFuncSlot_12_00405db0();
        OID__FreeObject_Callback(*(void **)((int)this + 0x10));
        *(void **)((int)this + 0x18) = (void *)((int)extraout_EAX + iVar3 * 4);
        iVar3 = CFastVB__CountDwordsFromPointerSpan((int)this + 0xc);
        *(int *)((int)this + 0x14) = (int)extraout_EAX + iVar3 * 4 + 4;
        *(void **)((int)this + 0x10) = extraout_EAX;
      }
      else {
        CFastVB__CopyDwordRange(puVar5,puVar5,puVar5 + 1);
        CTexture__Helper_00573ff0
                  (*(void **)((int)this + 0x14),
                   1 - ((int)*(void **)((int)this + 0x14) - (int)puVar5 >> 2),puVar1);
        puVar2 = *(undefined4 **)((int)this + 0x14);
        for (; puVar5 != puVar2; puVar5 = puVar5 + 1) {
          *puVar5 = *puVar1;
        }
        *(int *)((int)this + 0x14) = *(int *)((int)this + 0x14) + 4;
      }
      local_c = local_c + 1;
    } while (local_c < param_2);
  }
  return;
}
