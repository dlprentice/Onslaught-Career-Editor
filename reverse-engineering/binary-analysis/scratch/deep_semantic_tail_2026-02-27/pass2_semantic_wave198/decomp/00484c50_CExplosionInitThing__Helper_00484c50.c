/* address: 0x00484c50 */
/* name: CExplosionInitThing__Helper_00484c50 */
/* signature: void __fastcall CExplosionInitThing__Helper_00484c50(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CExplosionInitThing__Helper_00484c50(int param_1)

{
  float fVar1;
  undefined4 *puVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  float *extraout_EAX;
  void *pvVar6;
  undefined **ppuVar7;
  float *extraout_EAX_00;
  int iVar8;
  undefined *puVar9;
  float fVar10;
  int *piVar11;
  float10 fVar12;
  double dVar13;
  float unaff_retaddr;
  float *pfVar14;
  float fStack_b0;
  undefined8 uStack_a8;
  float fStack_9c;
  float fStack_98;
  float fStack_94;
  float fStack_90;
  float fStack_8c;
  float fStack_84;
  float local_80;
  float fStack_7c;
  float fStack_70;
  float local_6c [3];
  int *apiStack_60 [2];
  int *piStack_58;
  int *apiStack_50 [2];
  int *piStack_48;
  int *apiStack_40 [2];
  int *piStack_38;
  int *apiStack_30 [2];
  int *piStack_28;
  float fStack_20;
  float fStack_1c;
  void *pvStack_10;
  void *pvStack_c;
  undefined1 *puStack_8;
  float fStack_4;

  fStack_4 = -NAN;
  puStack_8 = &LAB_005d2da0;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  CExplosionInitThing__SetupOverlayMarkerRenderState();
  iVar5 = CExplosionInitThing__CheckValueRange_852_899(0x8a9a98);
  fVar1 = _DAT_008aa4ec;
  if ((iVar5 != 0) && (*(int *)(param_1 + 0x58) == 0)) {
    fVar1 = _DAT_0067a62c + _DAT_008aa4ec;
  }
  pfVar14 = local_6c;
  local_80 = ((fVar1 + _DAT_008aa4f4) - _DAT_005dbe74) - _DAT_0067a62c;
  (*(code *)**(undefined4 **)(*(int *)(param_1 + 0x50) + 8))();
  CExplosionInitThing__InterpolateWrappedEulerFromHistory
            (*(void **)(param_1 + 0x50),(int)&uStack_a8,pfVar14);
  fVar12 = (float10)fsin(-(float10)*extraout_EAX);
  fVar1 = (float)((fVar12 * (float10)_DAT_005d8610) / (float10)unaff_retaddr);
  fVar12 = (float10)fcos(-(float10)*extraout_EAX);
  fStack_9c = (float)((fVar12 * (float10)_DAT_005d8610) / (float10)unaff_retaddr);
  CSPtrSet__Init(apiStack_50);
  puStack_8 = (undefined1 *)0x0;
  CSPtrSet__Init(apiStack_30);
  puStack_8._0_1_ = 1;
  CSPtrSet__Init(apiStack_40);
  puStack_8._0_1_ = 2;
  CSPtrSet__Init(apiStack_60);
  puStack_8 = (undefined1 *)CONCAT31(puStack_8._1_3_,3);
  puVar2 = DAT_008550d0;
  if (DAT_008550d0 == (undefined4 *)0x0) {
    piVar11 = (int *)0x0;
  }
  else {
    piVar11 = (int *)*DAT_008550d0;
  }
  while (piVar11 != (int *)0x0) {
    iVar5 = (**(code **)(*piVar11 + 0x1a4))();
    if ((iVar5 != 0) && ((*(byte *)(piVar11 + 0xb) & 4) == 0)) {
      if ((*(byte *)(piVar11 + 0xd) & 8) == 0) {
        if (piVar11[0x7d] == 0) {
          if (piVar11[0x4e] == 1) {
            CSPtrSet__AddToTail(apiStack_40,piVar11);
          }
          else if (piVar11[0x4e] == 0) {
            CSPtrSet__AddToTail(apiStack_60,piVar11);
          }
          else {
            iVar5 = (**(code **)(*piVar11 + 0x68))();
            if (((iVar5 == 0) && ((*(byte *)(piVar11 + 0xb) & 0x10) == 0)) && (piVar11[0xc] != 0)) {
              (**(code **)piVar11[2])(&local_80);
              fStack_98 = local_80 - fStack_70;
              fStack_94 = fStack_7c - local_6c[0];
              fVar3 = fStack_98 * fStack_9c - fStack_94 * fVar1;
              fStack_8c = fStack_98 * fVar1 + fStack_94 * fStack_9c;
              fVar10 = fVar3 * fVar3 + fStack_8c * fStack_8c;
              if (fVar10 < _DAT_005dbe70) {
                fVar10 = SQRT(fVar10);
                iVar5 = -0x1000000;
                fVar4 = _DAT_005dbe6c / fVar10;
                if (fVar4 < _DAT_005d8568) {
                  fVar3 = fVar4 * fVar3;
                  fStack_8c = fVar4 * fStack_8c;
                  uStack_a8 = (longlong)
                              ROUND((_DAT_005d8568 - (fVar10 - _DAT_005dbe6c) * _DAT_005dbe68) *
                                    _DAT_005d8c70);
                  iVar5 = (int)(float)uStack_a8 << 0x18;
                }
                fVar10 = (float)((int)&PTR_BYTE_00606060 +
                                iVar5 + (-(uint)((piVar11[0xd] & 0x400U) != 0) & 0x101010));
                fVar3 = (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbb70 + fVar3) - _DAT_005d8568;
                fStack_b0 = ((fStack_84 - _DAT_005d857c) - fStack_8c) + _DAT_005d8568;
                pvVar6 = (void *)CExplosionInitThing__Helper_00485830
                                           ((void *)param_1,(int)piVar11,(int)fVar10);
                CExplosionInitThing__Helper_004857e0(fVar3,fStack_b0,pvVar6,fVar10);
              }
            }
          }
        }
        else {
          CSPtrSet__AddToTail(apiStack_30,piVar11);
        }
      }
      else {
        CSPtrSet__AddToTail(apiStack_50,piVar11);
      }
    }
    puVar2 = (undefined4 *)puVar2[1];
    if (puVar2 == (undefined4 *)0x0) {
      piVar11 = (int *)0x0;
    }
    else {
      piVar11 = (int *)*puVar2;
    }
  }
  piStack_58 = apiStack_60[0];
  if (apiStack_60[0] == (int *)0x0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *apiStack_60[0];
  }
  while (iVar5 != 0) {
    (*(code *)**(undefined4 **)(iVar5 + 8))(&local_80);
    fStack_90 = local_80 - fStack_70;
    fStack_8c = fStack_7c - local_6c[0];
    fVar3 = fStack_90 * fStack_9c - fStack_8c * fVar1;
    fStack_94 = fStack_90 * fVar1 + fStack_8c * fStack_9c;
    fVar10 = fVar3 * fVar3 + fStack_94 * fStack_94;
    if (fVar10 < _DAT_005dbe70) {
      fVar10 = SQRT(fVar10);
      iVar8 = -0x1000000;
      fVar4 = _DAT_005dbe6c / fVar10;
      if (fVar4 < _DAT_005d8568) {
        fVar3 = fVar4 * fVar3;
        fStack_94 = fVar4 * fStack_94;
        uStack_a8 = (longlong)
                    ROUND((_DAT_005d8568 - (fVar10 - _DAT_005dbe6c) * _DAT_005dbe68) * _DAT_005d8c70
                         );
        iVar8 = (int)(float)uStack_a8 << 0x18;
      }
      puVar9 = &DAT_005050af + iVar8 + (-(uint)((*(uint *)(iVar5 + 0x34) & 0x400) != 0) & 0x404050);
      fStack_b0 = (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbb70 + fVar3) - _DAT_005d8568;
      fVar3 = ((fStack_84 - _DAT_005d857c) - fStack_94) + _DAT_005d8568;
      pvVar6 = (void *)CExplosionInitThing__Helper_00485830((void *)param_1,iVar5,(int)puVar9);
      CExplosionInitThing__Helper_004857e0(fStack_b0,fVar3,pvVar6,(float)puVar9);
    }
    piStack_58 = (int *)piStack_58[1];
    if (piStack_58 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piStack_58;
    }
  }
  piStack_38 = apiStack_40[0];
  if (apiStack_40[0] == (int *)0x0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *apiStack_40[0];
  }
  while (iVar5 != 0) {
    (*(code *)**(undefined4 **)(iVar5 + 8))(&local_80);
    fStack_90 = local_80 - fStack_70;
    fStack_8c = fStack_7c - local_6c[0];
    fVar3 = fStack_90 * fStack_9c - fStack_8c * fVar1;
    fStack_94 = fStack_90 * fVar1 + fStack_8c * fStack_9c;
    fVar10 = fVar3 * fVar3 + fStack_94 * fStack_94;
    if (fVar10 < _DAT_005dbe70) {
      fVar10 = SQRT(fVar10);
      iVar8 = -0x1000000;
      fVar4 = _DAT_005dbe6c / fVar10;
      if (fVar4 < _DAT_005d8568) {
        fVar3 = fVar4 * fVar3;
        fStack_94 = fVar4 * fStack_94;
        uStack_a8 = (longlong)
                    ROUND((_DAT_005d8568 - (fVar10 - _DAT_005dbe6c) * _DAT_005dbe68) * _DAT_005d8c70
                         );
        iVar8 = (int)(float)uStack_a8 << 0x18;
      }
      fVar10 = (float)(iVar8 + (-(uint)((*(uint *)(iVar5 + 0x34) & 0x400) != 0) & 0x504848) +
                               0xaf0808);
      fStack_b0 = (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbb70 + fVar3) - _DAT_005d8568;
      fVar3 = ((fStack_84 - _DAT_005d857c) - fStack_94) + _DAT_005d8568;
      pvVar6 = (void *)CExplosionInitThing__Helper_00485830((void *)param_1,iVar5,(int)fVar10);
      CExplosionInitThing__Helper_004857e0(fStack_b0,fVar3,pvVar6,fVar10);
    }
    piStack_38 = (int *)piStack_38[1];
    if (piStack_38 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piStack_38;
    }
  }
  if (apiStack_30[0] == (int *)0x0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *apiStack_30[0];
  }
  piStack_28 = apiStack_30[0];
  if (iVar5 != 0) {
    fStack_b0 = fStack_84 - _DAT_005d857c;
    do {
      (*(code *)**(undefined4 **)(iVar5 + 8))(&local_80);
      fStack_90 = local_80 - fStack_70;
      fStack_8c = fStack_7c - local_6c[0];
      fVar3 = fStack_90 * fStack_9c - fStack_8c * fVar1;
      fVar4 = fStack_90 * fVar1 + fStack_8c * fStack_9c;
      fVar10 = _DAT_005dbe6c / SQRT(fVar3 * fVar3 + fVar4 * fVar4);
      if (fVar10 < _DAT_005d8568) {
        fVar3 = fVar10 * fVar3;
        fVar4 = fVar10 * fVar4;
      }
      uStack_a8 = CONCAT44(fVar4,(float)uStack_a8);
      iVar5 = *(int *)(iVar5 + 0x138);
      ppuVar7 = (undefined **)0x0;
      if (iVar5 == 0) {
        ppuVar7 = (undefined **)&DAT_005050af;
      }
      else if (iVar5 == 1) {
        ppuVar7 = (undefined **)0xaf0808;
      }
      else if (iVar5 == 2) {
        ppuVar7 = &PTR_BYTE_00606060;
      }
      fStack_98 = (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbb70 + fVar3) - _DAT_005d8568;
      CExplosionInitThing__Helper_004857e0
                (fStack_98,(fStack_b0 - fVar4) + _DAT_005d8568,*(void **)(param_1 + 0x1ac),
                 (float)(ppuVar7 + -0x400000));
      piStack_28 = (int *)piStack_28[1];
      if (piStack_28 == (int *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *piStack_28;
      }
    } while (iVar5 != 0);
  }
  DAT_00855148 = DAT_00855140;
  if (DAT_00855140 == (int *)0x0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *DAT_00855140;
  }
  if (iVar5 != 0) {
    fStack_b0 = fStack_84 - _DAT_005d857c;
    do {
      (*(code *)**(undefined4 **)(iVar5 + 8))(&local_80);
      fVar3 = local_80 - fStack_70;
      fVar10 = fStack_7c - local_6c[0];
      uStack_a8 = CONCAT44(fVar10,fVar3);
      fVar4 = fVar3 * fStack_9c - fVar10 * fVar1;
      fStack_8c = fVar3 * fVar1 + fVar10 * fStack_9c;
      fVar3 = _DAT_005dbe6c / SQRT(fVar4 * fVar4 + fStack_8c * fStack_8c);
      if (fVar3 < _DAT_005d8568) {
        fVar4 = fVar3 * fVar4;
        fStack_8c = fVar3 * fStack_8c;
      }
      fVar10 = -NAN;
      fVar3 = (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbb70 + fVar4) - _DAT_005d8568;
      fStack_98 = (fStack_b0 - fStack_8c) + _DAT_005d8568;
      pvVar6 = (void *)CExplosionInitThing__Helper_00485830((void *)param_1,iVar5,-0x100);
      CExplosionInitThing__Helper_004857e0(fVar3,fStack_98,pvVar6,fVar10);
      DAT_00855148 = (int *)DAT_00855148[1];
      if (DAT_00855148 == (int *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *DAT_00855148;
      }
    } while (iVar5 != 0);
  }
  piStack_48 = apiStack_50[0];
  if (apiStack_50[0] == (int *)0x0) {
    iVar5 = 0;
  }
  else {
    iVar5 = *apiStack_50[0];
  }
  if (iVar5 != 0) {
    fStack_b0 = fStack_84 - _DAT_005d857c;
    do {
      (*(code *)**(undefined4 **)(iVar5 + 8))(&local_80);
      fVar3 = local_80 - fStack_70;
      fVar10 = fStack_7c - local_6c[0];
      uStack_a8 = CONCAT44(fVar10,fVar3);
      fVar4 = fVar3 * fStack_9c - fVar10 * fVar1;
      fStack_8c = fVar3 * fVar1 + fVar10 * fStack_9c;
      fVar3 = _DAT_005dbe6c / SQRT(fVar4 * fVar4 + fStack_8c * fStack_8c);
      if (fVar3 < _DAT_005d8568) {
        fVar4 = fVar3 * fVar4;
        fStack_8c = fVar3 * fStack_8c;
      }
      fStack_98 = (fStack_b0 - fStack_8c) + _DAT_005d8568;
      CExplosionInitThing__Helper_004857e0
                ((_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbb70 + fVar4) - _DAT_005d8568,fStack_98,
                 *(void **)(param_1 + 0x1a4),-NAN);
      piStack_48 = (int *)piStack_48[1];
      if (piStack_48 == (int *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *piStack_48;
      }
    } while (iVar5 != 0);
  }
  if ((*(int *)(DAT_008a9d84 + 8) != 0) &&
     (iVar5 = *(int *)(*(int *)(DAT_008a9d84 + 8) + 0x30), iVar5 != 0)) {
    pfVar14 = &fStack_20;
    (*(code *)**(undefined4 **)(*(int *)(param_1 + 0x50) + 8))();
    CExplosionInitThing__InterpolateWrappedEulerFromHistory
              (*(void **)(param_1 + 0x50),(int)&fStack_94,pfVar14);
    fsin(-(float10)*extraout_EAX_00);
    fVar12 = (float10)fcos(-(float10)*extraout_EAX_00);
    fVar1 = (float)((fVar12 * (float10)_DAT_005d8610) / (float10)fStack_4);
    (*(code *)**(undefined4 **)(iVar5 + 8))();
    uStack_a8._0_4_ = local_80 - fStack_20;
    fVar3 = (float)uStack_a8 * fStack_b0 - (fStack_7c - fStack_1c) * fVar1;
    uStack_a8._4_4_ = (float)uStack_a8 * fVar1 + (fStack_7c - fStack_1c) * fStack_b0;
    fVar1 = _DAT_005dbe6c / SQRT(fVar3 * fVar3 + uStack_a8._4_4_ * uStack_a8._4_4_);
    if (fVar1 < _DAT_005d8568) {
      fVar3 = fVar1 * fVar3;
      uStack_a8._4_4_ = fVar1 * uStack_a8._4_4_;
    }
    fVar10 = -NAN;
    fVar1 = (_DAT_0067a628 + _DAT_008aa4f0 + _DAT_005dbb70 + fVar3) - _DAT_005d8568;
    fStack_98 = ((fStack_84 - _DAT_005d857c) - uStack_a8._4_4_) + _DAT_005d8568;
    dVar13 = CDXEngine__Helper_0055dfe7
                       ((double)*(float *)(param_1 + 400 + *(int *)(param_1 + 0x58) * 4));
    uStack_a8 = (longlong)ROUND(dVar13);
    CExplosionInitThing__Helper_004857e0
              (fVar1,fStack_98,*(void **)(param_1 + 0x178 + (int)(float)uStack_a8 * 4),fVar10);
  }
  D3DStateCache__SetStateCached(0,1,4);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  piVar11 = &DAT_0067a548;
  if (&DAT_0067a548 < PTR_DAT_0062ce70) {
    do {
      iVar5 = *piVar11;
      CVBufTexture__Render(1);
      if (iVar5 != 0) {
        CDXEngine__Helper_00501310(iVar5);
      }
      piVar11 = piVar11 + 1;
    } while (piVar11 < PTR_DAT_0062ce70);
  }
  D3DStateCache__SetSlotMode4or5(0);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  PTR_DAT_0062ce70 = (undefined *)&DAT_0067a548;
  puStack_8._0_1_ = 2;
  CSPtrSet__Clear(apiStack_60);
  puStack_8._0_1_ = 1;
  CSPtrSet__Clear(apiStack_40);
  puStack_8 = (undefined1 *)((uint)puStack_8._1_3_ << 8);
  CSPtrSet__Clear(apiStack_30);
  puStack_8 = (undefined1 *)0xffffffff;
  CSPtrSet__Clear(apiStack_50);
  ExceptionList = pvStack_10;
  return;
}
