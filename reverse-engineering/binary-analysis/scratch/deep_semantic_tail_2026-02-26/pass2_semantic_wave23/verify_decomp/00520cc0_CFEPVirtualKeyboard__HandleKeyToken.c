/* address: 0x00520cc0 */
/* name: CFEPVirtualKeyboard__HandleKeyToken */
/* signature: void __thiscall CFEPVirtualKeyboard__HandleKeyToken(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CFEPVirtualKeyboard__HandleKeyToken(void *this,int param_1,void *param_2)

{
  ushort uVar1;
  ushort uVar2;
  bool bVar3;
  uint uVar4;
  void *pvVar5;
  void *this_00;
  undefined3 extraout_var;
  ushort *puVar6;
  int iVar7;
  short *psVar8;
  int iVar9;
  int unaff_EBX;
  int *out_extent_xy;
  int local_8 [2];

  if ((ushort)param_1 < 0x20) {
    switch(param_1 & 0xffff) {
    case 1:
      if (*(char *)((int)this + 0x48) != '\0') {
        *(undefined1 *)((int)this + 0x48) = 0;
      }
      if (0 < *(int *)((int)this + 0x44)) {
        *(int *)((int)this + 0x44) = *(int *)((int)this + 0x44) + -1;
        return;
      }
      break;
    case 2:
      if (*(char *)((int)this + 0x48) != '\0') {
        *(undefined1 *)((int)this + 0x48) = 0;
      }
      iVar7 = *(int *)((int)this + 0x44);
      iVar9 = WcsLen((short *)((int)this + 4));
      if ((iVar7 < iVar9) && (iVar7 < 0x1f)) {
        *(int *)((int)this + 0x44) = iVar7 + 1;
        return;
      }
      break;
    case 3:
      if (*(char *)((int)this + 0x48) != '\0') {
        *(undefined2 *)((int)this + 4) = 0;
        *(undefined4 *)((int)this + 0x44) = 0;
        *(undefined1 *)((int)this + 0x48) = 0;
        return;
      }
      if (0 < *(int *)((int)this + 0x44)) {
        iVar7 = *(int *)((int)this + 0x44) + -1;
        *(int *)((int)this + 0x44) = iVar7;
        psVar8 = (short *)((int)this + iVar7 * 2 + 4);
        if (*(short *)((int)this + iVar7 * 2 + 4) != 0) {
          do {
            *psVar8 = psVar8[1];
            psVar8 = psVar8 + 1;
          } while (*psVar8 != 0);
          return;
        }
      }
      break;
    case 4:
      *(uint *)((int)this + 0x50) = (uint)(*(int *)((int)this + 0x50) == 0);
      return;
    case 5:
      *(uint *)((int)this + 0x4c) = (uint)(*(int *)((int)this + 0x4c) == 0);
      return;
    case 6:
      *(undefined4 *)((int)this + 0x6e4) = 0;
      return;
    case 7:
      *(undefined4 *)((int)this + 0x6e4) = 1;
      return;
    case 8:
      *(undefined4 *)((int)this + 0x6e4) = 2;
      return;
    case 9:
      CUnitAI__Helper_0055e64e(&DAT_008a1388,(void *)((int)this + 4));
      DAT_008a9580 = 1;
      DAT_008a9584 = 0;
      CFrontEnd__SetPage(&DAT_0089d758,0xb,0x14);
    }
  }
  else {
    psVar8 = (short *)((int)this + 4);
    uVar4 = WcsLen(psVar8);
    if (uVar4 < 0x1f) {
      if (*(char *)((int)this + 0x48) != '\0') {
        *psVar8 = 0;
        *(undefined4 *)((int)this + 0x44) = 0;
        *(undefined1 *)((int)this + 0x48) = 0;
      }
      uVar4 = WcsLen(psVar8);
      if (uVar4 < 0x20) {
        out_extent_xy = local_8;
        pvVar5 = CPlatform__Font(&DAT_0088a0a8,0);
        CDXFont__GetTextExtent(pvVar5,psVar8,out_extent_xy);
        if ((float)local_8[0] < _DAT_0089bcb8) {
          iVar7 = *(int *)((int)this + 0x44);
          pvVar5 = (void *)param_1;
          this_00 = CPlatform__Font(&DAT_0088a0a8,0);
          bVar3 = CFEPVirtualKeyboard__Helper_00465dd0(this_00,pvVar5,unaff_EBX);
          if (CONCAT31(extraout_var,bVar3) == 0) {
            switch(param_1 & 0xffff) {
            case 0xca:
            case 0xcb:
              param_1 = 0x45;
              break;
            case 0xce:
            case 0xcf:
              param_1 = 0x49;
              break;
            case 0xd4:
              param_1 = 0x4f;
              break;
            case 0xdb:
              param_1 = 0x55;
            }
          }
          puVar6 = (ushort *)((int)this + iVar7 * 2 + 4);
          do {
            uVar1 = *puVar6;
            *puVar6 = (ushort)param_1;
            uVar2 = *puVar6;
            puVar6 = puVar6 + 1;
            param_1 = (uint)uVar1;
          } while (uVar2 != 0);
          *(int *)((int)this + 0x44) = *(int *)((int)this + 0x44) + 1;
        }
      }
      *(undefined4 *)((int)this + 0x50) = 0;
      return;
    }
  }
  return;
}
