/* address: 0x0044d6f0 */
/* name: CFrontEnd__Helper_0044d6f0 */
/* signature: void __fastcall CFrontEnd__Helper_0044d6f0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CFrontEnd__Helper_0044d6f0(void *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  uint uVar6;
  uint uVar7;
  short *psVar8;
  void *pvVar9;
  int iVar10;
  int *piVar11;
  int local_20;
  short *local_14;
  int local_8;
  int local_4;

  if (*(int *)((int)param_1 + 0x1f8c) == 0) {
    return;
  }
  fVar2 = *(float *)((int)param_1 + 0xc) * _DAT_005d85ec;
  fVar3 = *(float *)((int)param_1 + 4) - fVar2;
  fVar2 = fVar2 + *(float *)((int)param_1 + 4);
  fVar4 = *(float *)((int)param_1 + 0x10) * _DAT_005d85ec;
  fVar5 = *(float *)((int)param_1 + 8) - fVar4;
  fVar1 = *(float *)((int)param_1 + 8);
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  if (*(int *)param_1 != 0) {
    CFrontEnd__DrawPanel();
    iVar10 = *(int *)((int)param_1 + 0x1f98);
    if ((((iVar10 == 1) || (iVar10 == 3)) || (iVar10 == 4)) &&
       (uVar6 = Input__GetClickStateInRect(fVar3,fVar5,fVar2,fVar4 + fVar1), (char)uVar6 != '\0')) {
      CFrontEnd__Helper_0044dd60(param_1,0x2c,0x3f800000);
    }
    CFrontEnd__DrawBox();
  }
  local_20 = 0;
  if (0 < *(int *)((int)param_1 + 0x1f64)) {
    local_14 = (short *)((int)param_1 + 0x1c);
    do {
      CDXFont__GetTextExtent(*(void **)((int)param_1 + 0x1f5c),local_14,&local_8);
      CDXEngine__DrawTextScaledWithShadow();
      local_20 = local_20 + 1;
      local_14 = local_14 + 100;
    } while (local_20 < *(int *)((int)param_1 + 0x1f64));
  }
  if (*(int *)((int)param_1 + 0x1f90) != 0) {
    CFrontEnd__DrawBarGraph();
    return;
  }
  iVar10 = *(int *)((int)param_1 + 0x1f98);
  if (iVar10 != 1) {
    if (iVar10 == 2) {
      piVar11 = &local_8;
      psVar8 = CFEPSaveGame__Helper_0046a2a0(0x1c - (uint)(*(int *)((int)param_1 + 0x1fa0) != 0));
      pvVar9 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar9,psVar8,piVar11);
      CFrontEnd__DrawPanel();
      iVar10 = 0;
      uVar6 = 1;
      do {
        fVar1 = (float)(int)(uVar6 * local_4) +
                (float)(*(int *)((int)param_1 + 0x1f60) * *(int *)((int)param_1 + 0x1f64)) + fVar5 +
                _DAT_005d8c44;
        uVar7 = Input__GetCursorStateInRectAndConsume(fVar3,fVar1,fVar2,(float)local_4 + fVar1);
        if ((char)uVar7 != '\0') {
          *(int *)((int)param_1 + 0x1fa0) = iVar10;
          break;
        }
        uVar7 = Input__GetClickStateInRect(fVar3,fVar1,fVar2,(float)local_4 + fVar1);
        if ((char)uVar7 != '\0') {
          CFrontEnd__PlaySound(1);
          *(int *)((int)param_1 + 0x1fa0) = iVar10;
          *(int *)((int)param_1 + 0x1fa4) = iVar10;
          *(undefined4 *)((int)param_1 + 0x1f7c) = 0;
          *(undefined4 *)((int)param_1 + 0x1f80) = 2;
          *(undefined4 *)((int)param_1 + 0x1fa8) = 0xfffffffe;
          break;
        }
        iVar10 = iVar10 + 1;
        uVar6 = uVar6 - 1;
      } while (uVar6 < 0x80000000);
      piVar11 = &local_8;
      psVar8 = CFEPSaveGame__Helper_0046a2a0(0x1b);
      pvVar9 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar9,psVar8,piVar11);
      CFEPSaveGame__Helper_0046a2a0(0x1b);
      CPlatform__Font(&DAT_0088a0a8,0);
      CDXEngine__DrawTextScaledWithShadow();
      piVar11 = &local_8;
      psVar8 = CFEPSaveGame__Helper_0046a2a0(0x1c);
      pvVar9 = CPlatform__Font(&DAT_0088a0a8,0);
      CDXFont__GetTextExtent(pvVar9,psVar8,piVar11);
      CFEPSaveGame__Helper_0046a2a0(0x1c);
      goto LAB_0044dd3a;
    }
    if (iVar10 != 3) {
      return;
    }
  }
  piVar11 = &local_8;
  psVar8 = CFEPSaveGame__Helper_0046a2a0(0x1d);
  pvVar9 = CPlatform__Font(&DAT_0088a0a8,0);
  CDXFont__GetTextExtent(pvVar9,psVar8,piVar11);
  CFrontEnd__DrawPanel();
  CFEPSaveGame__Helper_0046a2a0(0x1d);
LAB_0044dd3a:
  CPlatform__Font(&DAT_0088a0a8,0);
  CDXEngine__DrawTextScaledWithShadow();
  return;
}
