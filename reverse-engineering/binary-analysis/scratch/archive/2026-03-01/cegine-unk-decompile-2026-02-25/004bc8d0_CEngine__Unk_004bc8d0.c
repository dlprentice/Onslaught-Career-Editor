/* address: 0x004bc8d0 */
/* name: CEngine__Unk_004bc8d0 */
/* signature: void CEngine__Unk_004bc8d0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CEngine__Unk_004bc8d0(void)

{
  byte *pbVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  uint uVar5;
  int iVar6;
  void *pvVar7;
  int unaff_EDI;
  int iVar8;
  float10 extraout_ST0;
  float10 fVar9;
  double dVar10;
  uint local_34;
  int local_2c;
  float local_20;
  float local_1c;
  undefined4 local_18;
  undefined1 local_10 [16];

  fVar4 = DAT_006fbdfc;
  local_2c = 0;
  do {
    iVar8 = 0;
    fVar3 = (float)local_2c + _DAT_005d85ec;
    do {
      fVar2 = DAT_006fbdf4;
      local_20 = (float)iVar8 + _DAT_005d85ec;
      local_18 = 0;
      local_34 = (uint)(longlong)ROUND(fVar3);
      uVar5 = local_34;
      local_34 = (uint)(longlong)ROUND(local_20);
      local_1c = fVar3;
      uVar5 = CHeightField__Unk_0047ea20(0x6fadc8,local_34,uVar5);
      pvVar7 = DAT_00855290;
      if ((float)(int)(short)uVar5 * fVar2 <= fVar4) {
        CHeightField__Unk_0047ec60(0x6fadc8,local_10,&local_20);
        dVar10 = SQRT__Wrapper_004026b0(local_10);
        if (dVar10 <= (double)_DAT_005d856c) {
          fVar9 = (float10)_DAT_005d856c;
        }
        else {
          CDXTexture__Unk_0055dcb0();
          fVar9 = extraout_ST0;
        }
        pvVar7 = DAT_00855290;
        fVar2 = (float)(fVar9 + (float10)_DAT_005d85e4);
        if ((float10)*(float *)((int)DAT_00855290 + 0x2000) < fVar9 + (float10)_DAT_005d85e4) {
          CEngine__Unk_004bdf70(DAT_00855290,iVar8 + -1,local_2c,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + -1,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8 + 1,local_2c,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + 1,0,unaff_EDI);
        }
        pvVar7 = DAT_00855294;
        if (*(float *)((int)DAT_00855294 + 0x2000) < fVar2) {
          CEngine__Unk_004bdf70(DAT_00855294,iVar8 + -1,local_2c,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + -1,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8 + 1,local_2c,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + 1,0,unaff_EDI);
        }
        pvVar7 = DAT_00855298;
        if (*(float *)((int)DAT_00855298 + 0x2000) < fVar2) {
          uVar5 = iVar8 + -1 >> 1;
          iVar6 = local_2c >> 1;
          if ((((-1 < (int)uVar5) && ((int)uVar5 < 0x100)) && (-1 < iVar6)) && (iVar6 < 0x100)) {
            uVar5 = uVar5 & 0x80000007;
            pbVar1 = (byte *)((iVar8 + -1 >> 4) * 0x100 + iVar6 + (int)DAT_00855298);
            if ((int)uVar5 < 0) {
              uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
            }
            *pbVar1 = *pbVar1 & -('\x01' << ((byte)uVar5 & 0x1f)) - 1U;
          }
          CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + -1,0,unaff_EDI);
          CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c,0,unaff_EDI);
          goto LAB_004bcbab;
        }
      }
      else {
        CEngine__Unk_004bdf70(DAT_00855290,iVar8 + -1,local_2c,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + -1,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8 + 1,local_2c,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + 1,0,unaff_EDI);
        pvVar7 = DAT_00855294;
        CEngine__Unk_004bdf70(DAT_00855294,iVar8 + -1,local_2c,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + -1,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8 + 1,local_2c,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + 1,0,unaff_EDI);
        pvVar7 = DAT_00855298;
        CEngine__Unk_004bdf70(DAT_00855298,iVar8 + -1,local_2c,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + -1,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c,0,unaff_EDI);
LAB_004bcbab:
        CEngine__Unk_004bdf70(pvVar7,iVar8 + 1,local_2c,0,unaff_EDI);
        CEngine__Unk_004bdf70(pvVar7,iVar8,local_2c + 1,0,unaff_EDI);
      }
      iVar8 = iVar8 + 1;
    } while (iVar8 < 0x1ff);
    local_2c = local_2c + 1;
    if (0x1fe < local_2c) {
      return;
    }
  } while( true );
}
