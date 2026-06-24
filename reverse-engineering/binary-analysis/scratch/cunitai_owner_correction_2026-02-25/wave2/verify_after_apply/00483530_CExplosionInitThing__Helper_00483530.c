/* address: 0x00483530 */
/* name: CExplosionInitThing__Helper_00483530 */
/* signature: void __fastcall CExplosionInitThing__Helper_00483530(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CExplosionInitThing__Helper_00483530(int param_1)

{
  bool bVar1;
  int iVar2;
  void *pvVar3;
  int iVar4;
  float fVar5;
  int iVar6;
  int iVar7;
  float *pfVar8;
  float *pfVar9;
  int unaff_EDI;
  int iVar10;
  float fVar11;
  double dVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  short *psVar16;
  short *psVar17;
  float fVar18;
  char *format;
  float transition;
  int *piVar19;
  int fade_out;
  int local_334;
  float local_32c;
  float local_328;
  float local_320;
  float local_314;
  int local_30c [2];
  int local_304;
  char local_300 [256];
  char local_200 [256];
  char local_100 [256];

  bVar1 = false;
  if (*(int *)(param_1 + 0x94) != 0x3f800000) {
    iVar2 = 0x20c;
    do {
      if (*(int *)((int)&DAT_00855090 + iVar2) != 0) {
        fVar5 = *(float *)(param_1 + 0x94) + _DAT_005d85c0;
        *(float *)(param_1 + 0x94) = fVar5;
        if (_DAT_005d8568 < fVar5) {
          *(undefined4 *)(param_1 + 0x94) = 0x3f800000;
        }
        goto LAB_0048370d;
      }
      iVar2 = iVar2 + 4;
    } while (iVar2 < 0x21c);
  }
  if (*(float *)(param_1 + 0x94) != _DAT_005d856c) {
    iVar2 = 0x20c;
    do {
      if (*(int *)((int)&DAT_00855090 + iVar2) != 0) goto LAB_0048364c;
      iVar2 = iVar2 + 4;
    } while (iVar2 < 0x21c);
    if (*(float *)(param_1 + 0x98) <= _DAT_005d856c) {
      fVar5 = *(float *)(param_1 + 0x94) - _DAT_005d85c0;
      *(float *)(param_1 + 0x94) = fVar5;
      if (fVar5 < _DAT_005d856c) {
        *(undefined4 *)(param_1 + 0x94) = 0;
      }
      goto LAB_0048370d;
    }
    fVar5 = -*(float *)(param_1 + 0x98) * _DAT_005d8cb4 + *(float *)(param_1 + 0x98);
    *(float *)(param_1 + 0x98) = fVar5;
    if (ABS(-fVar5) < _DAT_005d85ec) {
      *(undefined4 *)(param_1 + 0x98) = 0;
    }
    bVar1 = true;
  }
LAB_0048364c:
  pfVar9 = (float *)(param_1 + 0x68);
  iVar7 = 0;
  iVar2 = 0x20c;
  pfVar8 = pfVar9;
  do {
    if ((*(int *)((int)&DAT_00855090 + iVar2) == 0) && (*pfVar8 != _DAT_005d856c)) {
      pfVar9 = (float *)(param_1 + 0x68 + iVar7 * 0xc);
      fVar5 = *pfVar9 - DAT_008a9e20 * _DAT_005d8c68;
      *pfVar9 = fVar5;
      if (fVar5 < _DAT_005d856c) {
        *pfVar9 = 0.0;
      }
      goto LAB_0048370d;
    }
    iVar2 = iVar2 + 4;
    iVar7 = iVar7 + 1;
    pfVar8 = pfVar8 + 3;
  } while (iVar2 < 0x21c);
  iVar7 = 0;
  iVar2 = 0x20c;
  do {
    if ((*(int *)((int)&DAT_00855090 + iVar2) != 0) && (*pfVar9 < _DAT_005d8568)) {
      pfVar9 = (float *)(param_1 + 0x68 + iVar7 * 0xc);
      fVar5 = DAT_008a9e20 * _DAT_005d8c68 + *pfVar9;
      *pfVar9 = fVar5;
      if (_DAT_005d8568 < fVar5) {
        *pfVar9 = 1.0;
        *(undefined4 *)(param_1 + (iVar7 * 3 + 0x1b) * 4) = 0xbf800000;
      }
      break;
    }
    iVar2 = iVar2 + 4;
    iVar7 = iVar7 + 1;
    pfVar9 = pfVar9 + 3;
  } while (iVar2 < 0x21c);
LAB_0048370d:
  if (*(float *)(param_1 + 0x94) != _DAT_005d856c) {
    if (_DAT_005d8568 <= *(float *)(param_1 + 0x94)) {
      local_314 = 43.0;
      local_328 = 0.0;
      local_320 = 0.0;
      pfVar9 = (float *)(param_1 + 0x68);
      iVar2 = 0x22c;
      do {
        pvVar3 = CPlatform__Font(&DAT_0088a0a8,1);
        local_328 = (float)*(int *)((int)pvVar3 + 0x54) * *pfVar9 + local_328;
        if (*(int *)(&DAT_00855070 + iVar2) != 0) {
          psVar16 = *(short **)((int)&DAT_00855090 + iVar2);
          piVar19 = local_30c;
          pvVar3 = CPlatform__Font(&DAT_0088a0a8,1);
          CDXFont__GetTextExtent(pvVar3,psVar16,piVar19);
          if (local_320 < (float)local_30c[0]) {
            local_320 = (float)local_30c[0];
          }
        }
        iVar2 = iVar2 + 4;
        pfVar9 = pfVar9 + 3;
      } while (iVar2 < 0x23c);
      if ((local_328 != _DAT_005d856c) && (!bVar1)) {
        iVar2 = PLATFORM__GetWindowWidth();
        iVar7 = PLATFORM__GetWindowWidth();
        fVar5 = ((float)((0x4b - iVar2) + iVar7) + local_320) - _DAT_005d85d8;
        fVar11 = (fVar5 - *(float *)(param_1 + 0x98)) * _DAT_005d8cb4 + *(float *)(param_1 + 0x98);
        *(float *)(param_1 + 0x98) = fVar11;
        if (ABS(fVar5 - fVar11) < _DAT_005d85ec) {
          *(float *)(param_1 + 0x98) = fVar5;
        }
      }
      PLATFORM__GetWindowWidth();
      CUnitAI__Helper_00482210();
      if (*(int *)(param_1 + 0xb0) == 0) {
        fVar5 = *(float *)(param_1 + 0xac) - DAT_008a9e20 * _DAT_005d85c0;
        *(float *)(param_1 + 0xac) = fVar5;
        if (fVar5 < _DAT_005d8c40) {
          *(undefined4 *)(param_1 + 0xac) = 0x3ecccccd;
          *(undefined4 *)(param_1 + 0xb0) = 1;
        }
      }
      else {
        fVar5 = DAT_008a9e20 * _DAT_005d85c0 + *(float *)(param_1 + 0xac);
        *(float *)(param_1 + 0xac) = fVar5;
        if (_DAT_005d8568 < fVar5) {
          *(undefined4 *)(param_1 + 0xac) = 0x3f800000;
          *(undefined4 *)(param_1 + 0xb0) = 0;
        }
      }
      iVar7 = 0;
      iVar2 = 0x24c;
      pfVar9 = (float *)(param_1 + 100);
      do {
        if ((pfVar9[1] != 1.0) || (*(int *)(&DAT_00855050 + iVar2) == 0)) goto LAB_004842d0;
        dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
        if (dVar12 != (double)pfVar9[2]) {
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          pfVar9[2] = (float)dVar12;
          *pfVar9 = DAT_00672fd0;
        }
        local_32c = DAT_00672fd0 - *pfVar9;
        if (_DAT_005d856c <= local_32c) {
          if (_DAT_005d8568 < local_32c) {
            local_32c = 1.0;
          }
        }
        else {
          local_32c = 0.0;
        }
        if (*(int *)(&DAT_00855050 + iVar2) == 3) {
          local_32c = 1.0;
        }
        psVar16 = *(short **)(&DAT_00855070 + iVar2);
        piVar19 = local_30c;
        pvVar3 = CPlatform__Font(&DAT_0088a0a8,1);
        CDXFont__GetTextExtent(pvVar3,psVar16,piVar19);
        if (*(float *)(param_1 + 0x98) < (float)local_30c[0] - _DAT_005d85d8) goto LAB_004842d0;
        bVar1 = false;
        switch(*(undefined4 *)(&DAT_00855050 + iVar2)) {
        case 1:
          CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          format = &DAT_006245cc;
          goto LAB_00483a68;
        case 2:
          local_334 = (int)(longlong)ROUND(*(float *)((int)&DAT_00855090 + iVar2));
          CWorld__Unk_0050d760(&DAT_00855090,iVar7,local_334);
          sprintf(local_300,s__d___d__0062d324);
          CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          sprintf(local_100,&DAT_0062d320);
          sprintf(local_200,&DAT_0062d318);
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          if ((double)_DAT_005d8568 < ABS(dVar12 - (double)*(float *)((int)&DAT_00855090 + iVar2)))
          break;
LAB_00483f18:
          local_32c = *(float *)(param_1 + 0xac);
          bVar1 = true;
          local_328 = (_DAT_005d8568 - local_32c) * _DAT_005d8c70;
          local_334 = (int)(longlong)ROUND(local_32c * _DAT_005d8c70 + local_328);
          iVar10 = local_334 * 0x100;
          local_334 = (int)(longlong)ROUND(local_32c * _DAT_005d964c + local_328);
          local_304 = local_334;
          iVar4 = local_334 + iVar10;
          local_334 = (int)(longlong)ROUND(local_32c * _DAT_005dbb64 + local_328);
          local_320 = (float)local_334;
          iVar4 = iVar4 * 0x100 + local_334;
          local_334 = (int)(longlong)ROUND(local_32c * _DAT_005dbe50);
          fVar5 = (float)(iVar4 * 0x100 - local_334);
          goto LAB_00483af3;
        case 3:
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          local_334 = (int)(longlong)ROUND(dVar12);
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,local_334 % 10);
          local_334 = (int)(longlong)ROUND(dVar12);
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,(local_334 / 10) % 6);
          local_334 = (int)(longlong)ROUND(dVar12);
          CWorld__Unk_0050d760(&DAT_00855090,iVar7,(local_334 / 0x3c) % 10);
          sprintf(local_300,s__d_d__d_d_0062d33c);
          break;
        case 4:
          CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          format = &DAT_0062d348;
LAB_00483a68:
          sprintf(local_300,format);
          break;
        case 5:
          local_334 = (int)(longlong)ROUND(*(float *)((int)&DAT_00855090 + iVar2));
          CWorld__Unk_0050d760(&DAT_00855090,iVar7,local_334);
          sprintf(local_300,s__d___d__0062d324);
          CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          sprintf(local_100,&DAT_0062d320);
          sprintf(local_200,&DAT_0062d318);
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          if (ABS(dVar12 - (double)*(float *)((int)&DAT_00855090 + iVar2)) <=
              (double)*(float *)((int)&DAT_00855090 + iVar2) * (double)_DAT_005d8c1c)
          goto LAB_00483f18;
          break;
        case 6:
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,unaff_EDI);
          local_334 = (int)(longlong)ROUND(dVar12 * (double)_DAT_005db020);
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,local_334 % 10);
          local_334 = (int)(longlong)ROUND(dVar12 * (double)_DAT_005d85cc);
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,local_334 % 10);
          local_334 = (int)(longlong)ROUND(dVar12);
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,local_334 % 10);
          local_334 = (int)(longlong)ROUND(dVar12);
          dVar12 = CWorld__Unk_0050d760(&DAT_00855090,iVar7,(local_334 / 10) % 6);
          local_334 = (int)(longlong)ROUND(dVar12);
          CWorld__Unk_0050d760(&DAT_00855090,iVar7,(local_334 / 0x3c) % 10);
          sprintf(local_300,s__d_d__d_d__d_d_0062d32c);
        }
        local_328 = (_DAT_005d8568 - local_32c) * _DAT_005d8c70;
        local_334 = (int)(longlong)ROUND(local_32c * _DAT_005d8c70 + local_328);
        iVar10 = local_334 * 0x100;
        local_334 = (int)(longlong)ROUND(local_32c * _DAT_005d964c + local_328);
        local_304 = local_334;
        iVar4 = local_334 + iVar10;
        local_334 = (int)(longlong)ROUND(local_32c * _DAT_005dbb64 + local_328);
        iVar4 = iVar4 * 0x100 + local_334;
        local_320 = (float)local_334;
        local_334 = (int)(longlong)ROUND(local_32c * _DAT_005db4e4 + local_328);
        fVar5 = (float)(iVar4 * 0x100 + local_334);
LAB_00483af3:
        iVar4 = *(int *)(&DAT_00855070 + iVar2);
        fade_out = 0;
        fVar18 = 1.4013e-45;
        psVar16 = (short *)0x3f800000;
        fVar15 = 1.0;
        fVar14 = 1.0;
        fVar13 = 0.008;
        fVar11 = local_314;
        iVar6 = PLATFORM__GetWindowWidth();
        pvVar3 = (void *)((float)(iVar6 + -0xa5) - (float)local_30c[0]);
        CPlatform__Font(&DAT_0088a0a8,1);
        CDXFont__DrawTextDynamic
                  (pvVar3,fVar11,fVar13,fVar14,fVar15,fVar5,iVar4,psVar16,fVar18,fade_out,unaff_EDI)
        ;
        fVar5 = local_314;
        if ((*(int *)(&DAT_00855050 + iVar2) == 2) || (*(int *)(&DAT_00855050 + iVar2) == 5)) {
          if (bVar1) {
            local_32c = *(float *)(param_1 + 0xac);
            local_328 = (_DAT_005d8568 - local_32c) * _DAT_005d8c70;
            local_334 = (int)(longlong)ROUND(local_32c * _DAT_005d8c70 + local_328);
            iVar10 = local_334 * 0x100;
            local_334 = (int)(longlong)ROUND(local_32c * _DAT_005dbb64 + local_328);
            local_320 = (float)local_334;
            iVar4 = local_334 + iVar10;
            local_334 = (int)(longlong)ROUND(local_32c * _DAT_005d964c + local_328);
            iVar4 = local_334 + iVar4 * 0x100;
            local_334 = (int)(longlong)ROUND(local_32c * _DAT_005db5dc);
            fVar11 = (float)(iVar4 * 0x100 - local_334);
          }
          else {
            local_334 = (int)(longlong)ROUND(local_32c * _DAT_005db2b8 + local_328);
            fVar11 = (float)((((int)local_320 + iVar10) * 0x100 + local_304) * 0x100 + local_334);
          }
          piVar19 = local_30c;
          psVar16 = Text__AsciiToWideScratch(local_300);
          pvVar3 = CPlatform__Font(&DAT_0088a0a8,1);
          CDXFont__GetTextExtent(pvVar3,psVar16,piVar19);
          iVar6 = 0;
          transition = 1.4013e-45;
          psVar17 = (short *)0x3f800000;
          psVar16 = Text__AsciiToWideScratch(local_100);
          fVar18 = 1.0;
          fVar15 = 1.0;
          fVar14 = 0.008;
          fVar13 = local_314;
          iVar4 = PLATFORM__GetWindowWidth();
          pvVar3 = (void *)((float)(iVar4 + -0x55) - (float)local_30c[0]);
          CPlatform__Font(&DAT_0088a0a8,1);
          CDXFont__DrawTextDynamic
                    (pvVar3,fVar13,fVar14,fVar15,fVar18,fVar11,(int)psVar16,psVar17,transition,iVar6
                     ,unaff_EDI);
          if (bVar1) {
            fVar11 = *(float *)(param_1 + 0xac);
            fVar13 = (_DAT_005d8568 - fVar11) * _DAT_005d8c70;
            local_334 = (int)(longlong)ROUND(fVar11 * _DAT_005d8c70 + fVar13);
            iVar4 = local_334 * 0x100;
            local_334 = (int)(longlong)ROUND(fVar11 * _DAT_005dbe4c + fVar13);
            iVar4 = iVar4 + local_334;
            local_334 = (int)(longlong)ROUND(fVar11 * _DAT_005dbb64 + fVar13);
            iVar4 = iVar4 * 0x100 + local_334;
            local_334 = (int)(longlong)ROUND(fVar11 * _DAT_005db5dc);
            fVar11 = (float)(iVar4 * 0x100 - local_334);
          }
          else {
            local_334 = (int)(longlong)ROUND(local_32c * _DAT_005dbe4c + local_328);
            iVar10 = local_334 + iVar10;
            local_334 = (int)(longlong)ROUND(local_32c * _DAT_005db2b8 + local_328);
            fVar11 = (float)((iVar10 * 0x100 + (int)local_320) * 0x100 + local_334);
          }
          piVar19 = local_30c;
          psVar16 = Text__AsciiToWideScratch(local_200);
          pvVar3 = CPlatform__Font(&DAT_0088a0a8,1);
          CDXFont__GetTextExtent(pvVar3,psVar16,piVar19);
          iVar10 = 0;
          fVar18 = 1.4013e-45;
          psVar17 = (short *)0x3f800000;
          psVar16 = Text__AsciiToWideScratch(local_200);
          fVar15 = 1.0;
          fVar14 = 1.0;
          fVar13 = 0.008;
          iVar4 = PLATFORM__GetWindowWidth();
        }
        else {
          if (bVar1) {
            fVar11 = *(float *)(param_1 + 0xac);
            fVar13 = (_DAT_005d8568 - fVar11) * _DAT_005d8c70;
            local_334 = (int)(longlong)ROUND(fVar11 * _DAT_005d8c70 + fVar13);
            iVar4 = local_334 * 0x100;
            local_334 = (int)(longlong)ROUND(fVar11 * _DAT_005dbb64 + fVar13);
            iVar4 = iVar4 + local_334;
            local_334 = (int)(longlong)ROUND(fVar11 * _DAT_005d964c + fVar13);
            iVar4 = iVar4 * 0x100 + local_334;
            local_334 = (int)(longlong)ROUND(fVar11 * _DAT_005db5dc);
            fVar11 = (float)(iVar4 * 0x100 - local_334);
          }
          else {
            local_334 = (int)(longlong)ROUND(local_32c * _DAT_005db2b8 + local_328);
            fVar11 = (float)(((iVar10 + (int)local_320) * 0x100 + local_304) * 0x100 + local_334);
          }
          piVar19 = local_30c;
          psVar16 = Text__AsciiToWideScratch(local_300);
          pvVar3 = CPlatform__Font(&DAT_0088a0a8,1);
          CDXFont__GetTextExtent(pvVar3,psVar16,piVar19);
          iVar10 = 0;
          fVar18 = 1.4013e-45;
          psVar17 = (short *)0x3f800000;
          psVar16 = Text__AsciiToWideScratch(local_300);
          fVar15 = 1.0;
          fVar14 = 1.0;
          fVar13 = 0.008;
          iVar4 = PLATFORM__GetWindowWidth();
        }
        pvVar3 = (void *)((float)(iVar4 + -0x55) - (float)local_30c[0]);
        CPlatform__Font(&DAT_0088a0a8,1);
        CDXFont__DrawTextDynamic
                  (pvVar3,fVar5,fVar13,fVar14,fVar15,fVar11,(int)psVar16,psVar17,fVar18,iVar10,
                   unaff_EDI);
LAB_004842d0:
        pvVar3 = CPlatform__Font(&DAT_0088a0a8,1);
        iVar2 = iVar2 + 4;
        iVar7 = iVar7 + 1;
        local_314 = (float)*(int *)((int)pvVar3 + 0x54) * pfVar9[1] + local_314;
        pfVar9 = pfVar9 + 3;
      } while (iVar2 < 0x25c);
    }
    else {
      PLATFORM__GetWindowWidth();
      CUnitAI__Helper_00482210();
    }
  }
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  return;
}
