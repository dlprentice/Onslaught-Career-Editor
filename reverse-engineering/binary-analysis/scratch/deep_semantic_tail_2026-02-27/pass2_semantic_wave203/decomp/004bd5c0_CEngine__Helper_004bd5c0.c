/* address: 0x004bd5c0 */
/* name: CEngine__Helper_004bd5c0 */
/* signature: void __cdecl CEngine__Helper_004bd5c0(int param_1, int param_2, int param_3, int param_4, int param_5) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CEngine__Helper_004bd5c0(int param_1,int param_2,int param_3,int param_4,int param_5)

{
  float fVar1;
  float fVar2;
  float fVar3;
  uint uVar4;
  void *pvVar5;
  int iVar6;
  uint uVar7;
  byte *pbVar8;
  int iVar9;
  int unaff_EDI;
  int iVar10;
  int iVar11;
  float10 extraout_ST0;
  float10 fVar12;
  double dVar13;
  uint local_28;
  float local_20;
  float local_1c;
  undefined4 local_18;
  undefined1 local_10 [16];

  if (param_1 < 0) {
    param_1 = 0;
  }
  if (param_2 < 0) {
    param_2 = 0;
  }
  if (0x1ff < param_3) {
    param_3 = 0x1ff;
  }
  iVar11 = param_2;
  fVar3 = DAT_006fbdfc;
  if (0x1ff < param_4) {
    param_4 = 0x1ff;
  }
  for (; DAT_006fbdfc = fVar3, iVar11 < param_4; iVar11 = iVar11 + 1) {
    if (param_1 < param_3) {
      iVar10 = iVar11 >> 1;
      iVar9 = param_1;
      do {
        uVar4 = iVar9 >> 1;
        iVar6 = iVar9 >> 4;
        if ((((-1 < (int)uVar4) && ((int)uVar4 < 0x100)) && (-1 < iVar10)) && (iVar10 < 0x100)) {
          pbVar8 = (byte *)(iVar6 * 0x100 + iVar10 + (int)DAT_00855290);
          uVar7 = uVar4 & 0x80000007;
          if ((int)uVar7 < 0) {
            uVar7 = (uVar7 - 1 | 0xfffffff8) + 1;
          }
          *pbVar8 = *pbVar8 | '\x01' << ((byte)uVar7 & 0x1f);
        }
        if (-1 < (int)uVar4) {
          if ((((int)uVar4 < 0x100) && (-1 < iVar10)) && (iVar10 < 0x100)) {
            pbVar8 = (byte *)(iVar6 * 0x100 + iVar10 + (int)DAT_00855294);
            uVar7 = uVar4 & 0x80000007;
            if ((int)uVar7 < 0) {
              uVar7 = (uVar7 - 1 | 0xfffffff8) + 1;
            }
            *pbVar8 = *pbVar8 | '\x01' << ((byte)uVar7 & 0x1f);
          }
          if (((-1 < (int)uVar4) && ((int)uVar4 < 0x100)) && ((-1 < iVar10 && (iVar10 < 0x100)))) {
            pbVar8 = (byte *)((int)DAT_00855298 + iVar6 * 0x100 + iVar10);
            uVar4 = uVar4 & 0x80000007;
            if ((int)uVar4 < 0) {
              uVar4 = (uVar4 - 1 | 0xfffffff8) + 1;
            }
            *pbVar8 = *pbVar8 | '\x01' << ((byte)uVar4 & 0x1f);
          }
        }
        iVar9 = iVar9 + 1;
      } while (iVar9 < param_3);
    }
    fVar3 = DAT_006fbdfc;
  }
  for (; param_2 < param_4; param_2 = param_2 + 1) {
    if (param_1 < param_3) {
      fVar2 = (float)param_2 + _DAT_005d85ec;
      iVar11 = param_1;
      do {
        fVar1 = DAT_006fbdf4;
        local_18 = 0;
        local_20 = (float)iVar11 + _DAT_005d85ec;
        local_28 = (uint)(longlong)ROUND(fVar2);
        uVar4 = local_28;
        local_28 = (uint)(longlong)ROUND(local_20);
        local_1c = fVar2;
        uVar4 = CWorld__Helper_0047ea20(0x6fadc8,local_28,uVar4);
        pvVar5 = DAT_00855290;
        if ((float)(int)(short)uVar4 * fVar1 <= fVar3) {
          CMonitor__Helper_0047ec60(0x6fadc8,local_10,&local_20);
          dVar13 = SQRT__Wrapper_004026b0(local_10);
          if (dVar13 <= (double)_DAT_005d856c) {
            fVar12 = (float10)_DAT_005d856c;
          }
          else {
            OID__Helper_0055dcb0();
            fVar12 = extraout_ST0;
          }
          pvVar5 = DAT_00855290;
          fVar1 = (float)(fVar12 + (float10)_DAT_005d85e4);
          if ((float10)*(float *)((int)DAT_00855290 + 0x2000) < fVar12 + (float10)_DAT_005d85e4) {
            CWorld__Helper_004bdf70(DAT_00855290,iVar11 + -1,param_2,0,unaff_EDI);
            CWorld__Helper_004bdf70(pvVar5,iVar11,param_2 + -1,0,unaff_EDI);
            CWorld__Helper_004bdf70(pvVar5,iVar11,param_2,0,unaff_EDI);
            CWorld__Helper_004bdf70(pvVar5,iVar11 + 1,param_2,0,unaff_EDI);
            CWorld__Helper_004bdf70(pvVar5,iVar11,param_2 + 1,0,unaff_EDI);
          }
          if (*(float *)((int)DAT_00855294 + 0x2000) < fVar1) {
            CWorld__Helper_004bd440(DAT_00855294,iVar11,param_2,unaff_EDI);
          }
          if (*(float *)((int)DAT_00855298 + 0x2000) < fVar1) {
            CWorld__Helper_004bd440(DAT_00855298,iVar11,param_2,unaff_EDI);
          }
        }
        else {
          iVar9 = iVar11 + 1;
          CWorld__Helper_004bdf70(DAT_00855290,iVar11 + -1,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2 + -1,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar9,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2 + 1,0,unaff_EDI);
          pvVar5 = DAT_00855294;
          CWorld__Helper_004bdf70(DAT_00855294,iVar11 + -1,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2 + -1,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar9,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2 + 1,0,unaff_EDI);
          pvVar5 = DAT_00855298;
          CWorld__Helper_004bdf70(DAT_00855298,iVar11 + -1,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2 + -1,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar9,param_2,0,unaff_EDI);
          CWorld__Helper_004bdf70(pvVar5,iVar11,param_2 + 1,0,unaff_EDI);
        }
        iVar11 = iVar11 + 1;
      } while (iVar11 < param_3);
    }
  }
  if (param_5 == 0) {
    DAT_00809590 = DAT_00809588;
    if (DAT_00809588 == (undefined4 *)0x0) {
      pvVar5 = (void *)0x0;
    }
    else {
      pvVar5 = (void *)*DAT_00809588;
    }
    while (pvVar5 != (void *)0x0) {
      CEngine__BuildStaticShadowVolumesAroundUnit(pvVar5);
      DAT_00809590 = (undefined4 *)DAT_00809590[1];
      if (DAT_00809590 == (undefined4 *)0x0) {
        pvVar5 = (void *)0x0;
      }
      else {
        pvVar5 = (void *)*DAT_00809590;
      }
    }
  }
  DAT_00809598 = 1;
  return;
}
