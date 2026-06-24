/* address: 0x00486e00 */
/* name: CExplosionInitThing__RenderWorldTargetSprites */
/* signature: void __fastcall CExplosionInitThing__RenderWorldTargetSprites(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CExplosionInitThing__RenderWorldTargetSprites(int param_1)

{
  float fVar1;
  byte bVar2;
  int *piVar3;
  int iVar4;
  bool bVar5;
  int iVar6;
  undefined4 *puVar7;
  int iVar8;
  float *pfVar9;
  byte *pbVar10;
  int *piVar11;
  int iVar12;
  byte *pbVar13;
  void *unaff_EDI;
  undefined4 *puVar14;
  bool bVar15;
  float10 fVar16;
  float10 fVar17;
  double dVar18;
  float in_stack_ffffff0c;
  float in_stack_ffffff10;
  float in_stack_ffffff14;
  float in_stack_ffffff18;
  float in_stack_ffffff1c;
  float in_stack_ffffff20;
  float in_stack_ffffff24;
  float in_stack_ffffff28;
  float in_stack_ffffff2c;
  float fVar19;
  float fVar20;
  float fVar21;
  float fStack_b4;
  int iStack_ac;
  float fStack_9c;
  undefined8 uStack_90;
  float fStack_88;
  float fStack_84;
  float local_80;
  float fStack_7c;
  float fStack_78;
  float fStack_74;
  float fStack_70;
  float fStack_6c;
  float local_60;
  float fStack_5c;

  puVar7 = (undefined4 *)(&DAT_0089d4a0 + *(int *)(param_1 + 0x58) * 0x40);
  puVar14 = &DAT_009c6914;
  for (iVar12 = 0x10; iVar12 != 0; iVar12 = iVar12 + -1) {
    *puVar14 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar14 = puVar14 + 1;
  }
  DAT_009c73e8 = 1;
  puVar7 = (undefined4 *)(&DAT_0089d520 + *(int *)(param_1 + 0x58) * 0x40);
  puVar14 = &DAT_009c6954;
  for (iVar12 = 0x10; iVar12 != 0; iVar12 = iVar12 + -1) {
    *puVar14 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar14 = puVar14 + 1;
  }
  DAT_009c73e9 = 1;
  puVar7 = (undefined4 *)(&DAT_0089d5a0 + *(int *)(param_1 + 0x58) * 0x40);
  puVar14 = &DAT_009c6994;
  for (iVar12 = 0x10; iVar12 != 0; iVar12 = iVar12 + -1) {
    *puVar14 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar14 = puVar14 + 1;
  }
  DAT_009c73ea = 1;
  CExplosionInitThing__SetupOverlayMarkerRenderState();
  fVar21 = 1.12104e-44;
  fVar20 = 3.22299e-44;
  fVar19 = 6.651793e-39;
  RenderState_Set(0x17,8);
  pfVar9 = (float *)(param_1 + 0x1b8 + *(int *)(param_1 + 0x58) * 4);
  *pfVar9 = DAT_008a9e20 * _DAT_005d8578 + *pfVar9;
  pfVar9 = (float *)(param_1 + 0x1b8 + *(int *)(param_1 + 0x58) * 4);
  if (_DAT_005d85e0 <= *(float *)(param_1 + 0x1b8 + *(int *)(param_1 + 0x58) * 4)) {
    *pfVar9 = *pfVar9 - _DAT_005d85e0;
  }
  puVar7 = &DAT_0067a5e8;
  puVar14 = (undefined4 *)&stack0xffffff0c;
  for (iVar12 = 0xc; iVar12 != 0; iVar12 = iVar12 + -1) {
    *puVar14 = *puVar7;
    puVar7 = puVar7 + 1;
    puVar14 = puVar14 + 1;
  }
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,DAT_0067a618,DAT_0067a61c,DAT_0067a620,DAT_0067a624,in_stack_ffffff0c,
             in_stack_ffffff10,in_stack_ffffff14,in_stack_ffffff18,in_stack_ffffff1c,
             in_stack_ffffff20,in_stack_ffffff24,in_stack_ffffff28,in_stack_ffffff2c,fVar19,fVar20,
             fVar21);
  iVar12 = *(int *)(param_1 + 0x50);
  piVar3 = (int *)(&DAT_0089c9a4)[DAT_0089ce4c];
  puVar7 = *(undefined4 **)(iVar12 + 0x294);
  *(undefined4 **)(iVar12 + 0x29c) = puVar7;
  if (puVar7 == (undefined4 *)0x0) {
    puVar7 = (undefined4 *)0x0;
  }
  else {
    puVar7 = (undefined4 *)*puVar7;
  }
  while (puVar7 != (undefined4 *)0x0) {
    if (((void *)*puVar7 != (void *)0x0) &&
       (CExplosionInitThing__Helper_004fd500((void *)*puVar7,&local_80,unaff_EDI),
       piVar3 != (int *)0x0)) {
      iVar6 = (**(code **)*piVar3)();
      fVar19 = local_80 - *(float *)(iVar6 + 4);
      fVar20 = fStack_7c - *(float *)(iVar6 + 8);
      iVar6 = (**(code **)(*piVar3 + 4))();
      if (_DAT_005d8580 <
          *(float *)(iVar6 + 4) * fVar19 +
          *(float *)(iVar6 + 0x24) * fStack_9c + *(float *)(iVar6 + 0x14) * fVar20) {
        CDXEngine__PushTransformState
                  (&DAT_009c65c0,(int)&uStack_90,(int)&local_80,*(float **)(param_1 + 0x54));
        dVar18 = CExplosionInitThing__ComputeNormalizedTimeInRange((int)puVar7);
        fVar19 = (float)dVar18;
        if (_DAT_005d8568 <= fVar19) {
          CVBufTexture__DrawSpriteEx
                    ((float)uStack_90,uStack_90._4_4_,0.013,*(void **)(param_1 + 0x1b0),4,0,1.0,0.0,
                     -524287.97,1.0,1.0,0.0,1.0,0.0,1.0);
          CVBufTexture__DrawSpriteEx
                    ((float)uStack_90,uStack_90._4_4_,0.013,*(void **)(param_1 + 0x1b4),4,0,1.0,
                     *(float *)(param_1 + 0x1b8 + *(int *)(param_1 + 0x58) * 4),-2.3448663e-38,1.0,
                     1.0,0.0,1.0,0.0,1.0);
        }
        else {
          fStack_b4 = (float)(longlong)ROUND(fVar19 * _DAT_005dbb80);
          fVar20 = (float)((int)fStack_b4 * -0x1000000 + 0xffffff);
          fVar19 = (_DAT_005d8568 - fVar19) * _DAT_005d85cc;
          fVar19 = fVar19 * fVar19;
          CVBufTexture__DrawSpriteEx
                    ((float)uStack_90,uStack_90._4_4_ - fVar19,0.013,*(void **)(param_1 + 0x1c8),4,0
                     ,1.0,0.0,fVar20,1.0,1.0,0.0,1.0,0.0,1.0);
          fVar16 = (float10)fcos((float10)_DAT_005dbea8);
          fVar17 = (float10)fsin((float10)_DAT_005dbea8);
          CVBufTexture__DrawSpriteEx
                    ((float)(fVar17 * (float10)fVar19) + (float)uStack_90,
                     uStack_90._4_4_ - (float)(fVar16 * (float10)fVar19),0.013,
                     *(void **)(param_1 + 0x1cc),4,0,1.0,0.0,fVar20,1.0,1.0,0.0,1.0,0.0,1.0);
          CVBufTexture__DrawSpriteEx
                    ((float)uStack_90 - (float)(fVar17 * (float10)fVar19),
                     uStack_90._4_4_ - (float)(fVar16 * (float10)fVar19),0.013,
                     *(void **)(param_1 + 0x1d0),4,0,1.0,0.0,fVar20,1.0,1.0,0.0,1.0,0.0,1.0);
        }
      }
    }
    puVar7 = *(undefined4 **)(*(int *)(iVar12 + 0x29c) + 4);
    *(undefined4 **)(iVar12 + 0x29c) = puVar7;
    if (puVar7 == (undefined4 *)0x0) {
      puVar7 = (undefined4 *)0x0;
    }
    else {
      puVar7 = (undefined4 *)*puVar7;
    }
  }
  iVar12 = *(int *)(param_1 + 0x50);
  puVar7 = *(undefined4 **)(iVar12 + 0x2a4);
  *(undefined4 **)(iVar12 + 0x2ac) = puVar7;
  if (puVar7 == (undefined4 *)0x0) {
    puVar7 = (undefined4 *)0x0;
  }
  else {
    puVar7 = (undefined4 *)*puVar7;
  }
  while (puVar7 != (undefined4 *)0x0) {
    if (((void *)*puVar7 != (void *)0x0) &&
       (CExplosionInitThing__Helper_004fd500((void *)*puVar7,&local_80,unaff_EDI),
       piVar3 != (int *)0x0)) {
      iVar6 = (**(code **)*piVar3)();
      fVar19 = local_80 - *(float *)(iVar6 + 4);
      fVar20 = fStack_7c - *(float *)(iVar6 + 8);
      iVar6 = (**(code **)(*piVar3 + 4))();
      if ((_DAT_005d8580 <
           *(float *)(iVar6 + 4) * fVar19 +
           *(float *)(iVar6 + 0x14) * fVar20 + *(float *)(iVar6 + 0x24) * fStack_9c) &&
         (CDXEngine__PushTransformState
                    (&DAT_009c65c0,(int)&uStack_90,(int)&local_80,*(float **)(param_1 + 0x54)),
         _DAT_005d856c < fStack_88)) {
        dVar18 = CExplosionInitThing__ComputeNormalizedTimeInRange((int)puVar7);
        fVar19 = (float)dVar18;
        fVar20 = _DAT_005d8568 - (float)dVar18 * _DAT_005d85ec;
        iStack_ac = (int)(longlong)ROUND((fVar19 + _DAT_005d8568) * _DAT_005d85ec * _DAT_005d9644);
        CVBufTexture__DrawSpriteEx
                  ((float)uStack_90,uStack_90._4_4_,0.013,*(void **)(param_1 + 0x1b4),4,0,1.0,
                   *(float *)(param_1 + 0x1b8 + *(int *)(param_1 + 0x58) * 4),
                   (float)(iStack_ac * -0x1000000 + 0xff5555),fVar20,fVar20,0.0,1.0,0.0,1.0);
        if (fVar19 < _DAT_005d8568) {
          iStack_ac = (int)(longlong)ROUND((_DAT_005d8568 - fVar19) * _DAT_005d9644);
          fVar20 = (float)(iStack_ac * -0x1000000 + 0xffffff);
          fVar19 = fVar19 * _DAT_005d85cc * fVar19 * _DAT_005d85cc;
          CVBufTexture__DrawSpriteEx
                    ((float)uStack_90,uStack_90._4_4_ - fVar19,0.013,*(void **)(param_1 + 0x1c8),4,0
                     ,1.0,0.0,fVar20,1.0,1.0,0.0,1.0,0.0,1.0);
          fVar16 = (float10)fcos((float10)_DAT_005dbea8);
          fVar17 = (float10)fsin((float10)_DAT_005dbea8);
          CVBufTexture__DrawSpriteEx
                    ((float)(fVar17 * (float10)fVar19) + (float)uStack_90,
                     uStack_90._4_4_ - (float)(fVar16 * (float10)fVar19),0.013,
                     *(void **)(param_1 + 0x1cc),4,0,1.0,0.0,fVar20,1.0,1.0,0.0,1.0,0.0,1.0);
          CVBufTexture__DrawSpriteEx
                    ((float)uStack_90 - (float)(fVar17 * (float10)fVar19),
                     uStack_90._4_4_ - (float)(fVar16 * (float10)fVar19),0.013,
                     *(void **)(param_1 + 0x1d0),4,0,1.0,0.0,fVar20,1.0,1.0,0.0,1.0,0.0,1.0);
        }
      }
    }
    puVar7 = *(undefined4 **)(*(int *)(iVar12 + 0x2ac) + 4);
    *(undefined4 **)(iVar12 + 0x2ac) = puVar7;
    if (puVar7 == (undefined4 *)0x0) {
      puVar7 = (undefined4 *)0x0;
    }
    else {
      puVar7 = (undefined4 *)*puVar7;
    }
  }
  iVar12 = *(int *)(*(int *)(param_1 + 0x50) + 0x2b8);
  if (iVar12 != 0) {
    piVar11 = *(int **)(iVar12 + 0x1c);
    *(int **)(iVar12 + 0x24) = piVar11;
    if (piVar11 == (int *)0x0) {
      iVar6 = 0;
    }
    else {
      iVar6 = *piVar11;
    }
    while (iVar6 != 0) {
      iVar4 = *(int *)(iVar6 + 0xc);
      if ((iVar4 != 0) && (piVar3 != (int *)0x0)) {
        iVar8 = (**(code **)*piVar3)();
        fVar19 = *(float *)(iVar4 + 0x20);
        fVar20 = *(float *)(iVar8 + 4);
        fVar21 = *(float *)(iVar4 + 0x24);
        fVar1 = *(float *)(iVar8 + 8);
        iVar8 = (**(code **)(*piVar3 + 4))();
        if (_DAT_005d8580 <
            *(float *)(iVar8 + 4) * (fVar19 - fVar20) +
            *(float *)(iVar8 + 0x14) * (fVar21 - fVar1) + *(float *)(iVar8 + 0x24) * fStack_9c) {
          (*(code *)**(undefined4 **)(iVar4 + 8))();
          CDXEngine__PushTransformState
                    (&DAT_009c65c0,(int)&local_80,(int)&local_60,*(float **)(param_1 + 0x54));
          if (_DAT_005d856c < fStack_78) {
            fVar19 = (DAT_008a9e44 * _DAT_005d8578 + DAT_00672fd0) - *(float *)(iVar6 + 0x10);
            if (_DAT_005d85ec < fVar19) {
              fVar19 = _DAT_005d85ec;
            }
            fVar20 = _DAT_005d85d8 - (fVar19 + fVar19) * _DAT_005dbea0;
            iStack_ac = (int)(longlong)ROUND((fVar19 + fVar19) * _DAT_005d9644);
            CVBufTexture__DrawSpriteEx
                      (local_80,fStack_7c,0.013,*(void **)(param_1 + 0x114),4,0,1.0,0.0,
                       (float)(iStack_ac * -0x1000000 + 0xffffff),fVar20,fVar20,0.0,1.0,0.0,1.0);
          }
        }
      }
      piVar11 = *(int **)(*(int *)(iVar12 + 0x24) + 4);
      *(int **)(iVar12 + 0x24) = piVar11;
      if (piVar11 == (int *)0x0) {
        iVar6 = 0;
      }
      else {
        iVar6 = *piVar11;
      }
    }
  }
  D3DStateCache__SetState114Raw(0,6,2);
  D3DStateCache__SetState114Raw(0,5,2);
  D3DStateCache__SetMipFilterLinear(0);
  RenderState_Set(0x13,2);
  RenderState_Set(0x14,2);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  DAT_00855148 = DAT_00855140;
  if (DAT_00855140 == (undefined4 *)0x0) {
    piVar11 = (int *)0x0;
  }
  else {
    piVar11 = (int *)*DAT_00855140;
  }
  do {
    if (piVar11 == (int *)0x0) {
      RenderState_Set(0x13,5);
      RenderState_Set(0x14,6);
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      return;
    }
    if ((*(byte *)(piVar11 + 0xd) & 0x10) == 0) {
      CUnitAI__Helper_004f3ac0(piVar11,(int)&fStack_70,unaff_EDI);
    }
    else {
      CExplosionInitThing__Helper_004fd500(piVar11,&fStack_70,unaff_EDI);
    }
    CDXEngine__PushTransformState
              (&DAT_009c65c0,(int)&local_60,(int)&fStack_70,*(float **)(param_1 + 0x54));
    PLATFORM__GetWindowWidth();
    PLATFORM__GetWindowHeight();
    bVar5 = false;
    if (piVar3 != (int *)0x0) {
      pfVar9 = (float *)(**(code **)*piVar3)();
      fStack_84 = fStack_74 - *pfVar9;
      local_80 = fStack_70 - pfVar9[1];
      fStack_7c = fStack_6c - pfVar9[2];
      iVar12 = (**(code **)(*piVar3 + 4))();
      bVar5 = true;
      if (_DAT_005d8580 <=
          *(float *)(iVar12 + 4) * local_80 +
          *(float *)(iVar12 + 0x14) * fStack_7c + *(float *)(iVar12 + 0x24) * fStack_78) {
        bVar5 = false;
      }
    }
    fStack_b4 = -2.5479637e+38;
    if ((piVar11[0xd] & 0x10U) == 0) {
      if ((piVar11[0xd] & 0x400000U) != 0) {
        if (piVar11[0x3b] == 0) goto LAB_004877f6;
        if (piVar11[0x3b] == 1) goto LAB_004878c4;
      }
    }
    else {
      iVar12 = piVar11[0x4e];
      if (iVar12 == 0) {
LAB_004877f6:
        fStack_b4 = -3.1901048e+38;
      }
      else if (iVar12 == 1) {
LAB_004878c4:
        fStack_b4 = -NAN;
      }
      else if ((iVar12 == 2) && ((DAT_008a9d38 == 0x2c6 || (DAT_008a9d38 == 0x2d0)))) {
        pbVar13 = &DAT_0062d350;
        pbVar10 = (byte *)(**(code **)(*piVar11 + 0xa4))();
        do {
          bVar2 = *pbVar10;
          bVar15 = bVar2 < *pbVar13;
          if (bVar2 != *pbVar13) {
LAB_004877ed:
            iVar12 = (1 - (uint)bVar15) - (uint)(bVar15 != 0);
            goto LAB_004877f2;
          }
          if (bVar2 == 0) break;
          bVar2 = pbVar10[1];
          bVar15 = bVar2 < pbVar13[1];
          if (bVar2 != pbVar13[1]) goto LAB_004877ed;
          pbVar10 = pbVar10 + 2;
          pbVar13 = pbVar13 + 2;
        } while (bVar2 != 0);
        iVar12 = 0;
LAB_004877f2:
        if (iVar12 == 0) goto LAB_004877f6;
      }
    }
    if ((piVar3 != (int *)0x0) && (!bVar5)) {
      (**(code **)*piVar3)();
      (**(code **)(*piVar11 + 0x40))();
      fVar16 = (float10)(**(code **)(*piVar3 + 0x10))();
      fVar19 = (float)((float10)0.0 / fVar16);
      if ((float10)_DAT_005d8604 <= (float10)0.0 / fVar16) {
        if (_DAT_005d85ec < fVar19) {
          uStack_90 = (longlong)ROUND((fVar19 - _DAT_005d85ec) * _DAT_005dbe9c);
          iVar12 = 0xff - (int)(float)uStack_90;
          if (iVar12 < 0) {
            iVar12 = 0;
          }
          fStack_b4 = (float)(((uint)fStack_b4 & 0xff000000) +
                             ((((uint)fStack_b4 >> 0x10 & 0xff) * iVar12 & 0xffffff00) +
                             (((uint)fStack_b4 >> 8 & 0xff) * iVar12 >> 8)) * 0x100 +
                             (((uint)fStack_b4 & 0xff) * iVar12 >> 8));
        }
      }
      else {
        fVar19 = 0.2;
      }
      CVBufTexture__DrawSpriteEx
                (local_60,fStack_5c,0.013,*(void **)(param_1 + 0x144),4,0,1.0,0.7853982,fStack_b4,
                 fVar19,fVar19,0.0,1.0,0.0,1.0);
    }
    DAT_00855148 = (undefined4 *)DAT_00855148[1];
    if (DAT_00855148 == (undefined4 *)0x0) {
      piVar11 = (int *)0x0;
    }
    else {
      piVar11 = (int *)*DAT_00855148;
    }
  } while( true );
}
