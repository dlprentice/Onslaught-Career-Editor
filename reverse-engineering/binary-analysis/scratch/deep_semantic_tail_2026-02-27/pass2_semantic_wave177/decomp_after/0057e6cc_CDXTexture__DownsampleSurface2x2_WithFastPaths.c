/* address: 0x0057e6cc */
/* name: CDXTexture__DownsampleSurface2x2_WithFastPaths */
/* signature: int __fastcall CDXTexture__DownsampleSurface2x2_WithFastPaths(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CDXTexture__DownsampleSurface2x2_WithFastPaths(void *param_1)

{
  int *piVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  int iVar14;
  float fVar15;
  int extraout_EAX;
  int extraout_EAX_00;
  float *extraout_EAX_01;
  int iVar16;
  void *extraout_EAX_02;
  void *extraout_EAX_03;
  void *pvVar17;
  void *pvVar18;
  float *pfVar19;
  float *pfVar20;
  float *pfVar21;
  float *pfVar22;
  uint uVar23;
  void *local_1c;
  float *local_18;
  float *local_14;
  uint local_10;
  void *local_8;

  if (*(char *)((int)param_1 + 8) != '\x05') {
    return -0x7fffbffb;
  }
  iVar16 = *(int *)param_1;
  uVar23 = *(uint *)(iVar16 + 0x1060);
  iVar14 = *(int *)((int)param_1 + 4);
  if ((((*(uint *)(iVar14 + 0x1060) != uVar23 >> 1) &&
       ((*(uint *)(iVar14 + 0x1060) != 1 || (uVar23 != 1)))) ||
      ((*(uint *)(iVar14 + 0x1064) != *(uint *)(iVar16 + 0x1064) >> 1 &&
       ((*(uint *)(iVar14 + 0x1064) != 1 || (*(int *)(iVar16 + 0x1064) != 1)))))) ||
     ((*(int *)(iVar14 + 0x1068) != 1 || (*(int *)(iVar16 + 0x1068) != 1)))) {
    return -0x7fffbffb;
  }
  if ((1 < uVar23) && ((uVar23 & 1) != 0)) {
    *(uint *)(iVar16 + 0x1060) = uVar23 & 0xfffffffe;
    piVar1 = (int *)(*(int *)param_1 + 0x106c);
    *piVar1 = *piVar1 - *(int *)(*(int *)param_1 + 0x1070);
  }
  uVar23 = *(uint *)(*(int *)param_1 + 0x1064);
  if (1 < uVar23) {
    *(uint *)(*(int *)param_1 + 0x1064) = uVar23 & 0xfffffffe;
  }
  if ((*(byte *)((int)param_1 + 10) & 8) != 0) goto switchD_0057e7e3_caseD_14;
  iVar16 = *(int *)param_1;
  iVar14 = *(int *)(iVar16 + 4);
  if ((((iVar14 != *(int *)(*(int *)((int)param_1 + 4) + 4)) || (*(uint *)(iVar16 + 0x1060) < 2)) ||
      (*(uint *)(iVar16 + 0x1064) < 2)) ||
     ((*(int *)(*(int *)((int)param_1 + 4) + 0x10) != 0 || (*(int *)(iVar16 + 0x10) != 0))))
  goto switchD_0057e7e3_caseD_14;
  if (iVar14 < 0x1e) {
    if (iVar14 == 0x1d) {
      iVar16 = CFastVB__Downsample2x1_A1R5G5B5(param_1);
    }
    else {
      switch(iVar14) {
      default:
        goto switchD_0057e7e3_caseD_14;
      case 0x15:
switchD_0057e7e3_caseD_15:
        CFastVB__DispatchMmxKernel_00657974(param_1);
        iVar16 = extraout_EAX_00;
        break;
      case 0x16:
switchD_0057e7e3_caseD_16:
        CFastVB__DispatchMmxKernel_00657978(param_1);
        iVar16 = extraout_EAX;
        break;
      case 0x17:
        iVar16 = CDXTexture__Average2x2Block_RGB565(param_1);
        break;
      case 0x18:
        iVar16 = CDXTexture__Average2x2Block_RGB555(param_1);
        break;
      case 0x19:
        iVar16 = CDXTexture__Average2x2Block_ARGB1555(param_1);
        break;
      case 0x1a:
        iVar16 = CDXTexture__Average2x2Block_A4R4G4B4(param_1);
        break;
      case 0x1b:
        iVar16 = CFastVB__Downsample2x1_R5G6B5(param_1);
        break;
      case 0x1c:
switchD_0057e7e3_caseD_1c:
        iVar16 = CFastVB__Downsample2x1_L8(param_1);
      }
    }
  }
  else if (iVar14 < 0x2a) {
    if (iVar14 == 0x29) goto switchD_0057e7e3_caseD_14;
    if (iVar14 != 0x1e) {
      if (iVar14 != 0x20) {
        if (iVar14 != 0x21) goto switchD_0057e7e3_caseD_14;
        goto switchD_0057e7e3_caseD_16;
      }
      goto switchD_0057e7e3_caseD_15;
    }
    iVar16 = CDXTexture__Average2x2Block_RGB444(param_1);
  }
  else {
    if (iVar14 == 0x32) goto switchD_0057e7e3_caseD_1c;
    if (iVar14 == 0x33) {
      iVar16 = CDXTexture__Average2x2Block_A8L8(param_1);
    }
    else {
      if (iVar14 != 0x34) goto switchD_0057e7e3_caseD_14;
      iVar16 = CDXTexture__Average2x2Block_A4L4(param_1);
    }
  }
  if (-1 < iVar16) {
    return 0;
  }
switchD_0057e7e3_caseD_14:
  iVar16 = *(int *)(*(int *)((int)param_1 + 4) + 0x1060);
  OID__AllocObject_DefaultTag_00662b2c(iVar16 << 4);
  if (extraout_EAX_01 == (float *)0x0) {
    local_14 = (float *)0x0;
  }
  else {
    _vector_constructor_iterator_(extraout_EAX_01,0x10,iVar16,CFastVB__ReturnInputInt);
    local_14 = extraout_EAX_01;
  }
  if (local_14 == (float *)0x0) {
    iVar16 = -0x7ff8fff2;
  }
  else {
    iVar16 = *(int *)(*(int *)param_1 + 0x1060);
    if (*(int *)(*(int *)param_1 + 0x1064) == 1) {
      OID__AllocObject_DefaultTag_00662b2c(iVar16 << 4);
      if (extraout_EAX_02 == (void *)0x0) {
        local_8 = (void *)0x0;
        pvVar17 = local_8;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX_02,0x10,iVar16,CFastVB__ReturnInputInt);
        pvVar17 = extraout_EAX_02;
        local_8 = extraout_EAX_02;
      }
    }
    else {
      OID__AllocObject_DefaultTag_00662b2c(iVar16 << 5);
      if (extraout_EAX_03 == (void *)0x0) {
        local_8 = (void *)0x0;
      }
      else {
        _vector_constructor_iterator_(extraout_EAX_03,0x10,iVar16 << 1,CFastVB__ReturnInputInt);
        local_8 = extraout_EAX_03;
      }
      pvVar17 = (void *)(*(int *)(*(int *)param_1 + 0x1060) * 0x10 + (int)local_8);
    }
    if (local_8 == (void *)0x0) {
      iVar16 = -0x7ff8fff2;
    }
    else {
      pvVar18 = pvVar17;
      local_1c = local_8;
      if (*(int *)(*(int *)param_1 + 0x1060) != 1) {
        local_1c = (void *)((int)local_8 + 0x10);
        pvVar18 = (void *)((int)pvVar17 + 0x10);
      }
      local_10 = 0;
      if (*(int *)(*(int *)((int)param_1 + 4) + 0x1064) != 0) {
        do {
          (**(code **)(**(int **)param_1 + 4))(local_10 * 2,0,local_8);
          if (pvVar17 != local_8) {
            (**(code **)(**(int **)param_1 + 4))(local_10 * 2 + 1,0,pvVar17);
          }
          fVar15 = _DAT_005e9328;
          uVar23 = 0;
          if (*(int *)(*(int *)((int)param_1 + 4) + 0x1060) != 0) {
            local_18 = local_14;
            do {
              iVar16 = uVar23 * 0x20;
              pfVar19 = (float *)((int)local_1c + iVar16);
              pfVar22 = (float *)((int)local_8 + iVar16);
              fVar2 = pfVar19[1];
              fVar3 = pfVar22[1];
              fVar4 = pfVar19[2];
              fVar5 = pfVar22[2];
              fVar6 = pfVar19[3];
              fVar7 = pfVar22[3];
              pfVar20 = (float *)((int)pvVar17 + iVar16);
              fVar8 = pfVar20[1];
              fVar9 = pfVar20[2];
              fVar10 = pfVar20[3];
              pfVar21 = (float *)((int)pvVar18 + iVar16);
              uVar23 = uVar23 + 1;
              fVar11 = pfVar21[1];
              fVar12 = pfVar21[2];
              fVar13 = pfVar21[3];
              *local_18 = (*pfVar19 + *pfVar22 + *pfVar20 + *pfVar21) * fVar15;
              local_18[1] = (fVar2 + fVar3 + fVar8 + fVar11) * fVar15;
              local_18[2] = (fVar4 + fVar5 + fVar9 + fVar12) * fVar15;
              local_18[3] = (fVar6 + fVar7 + fVar10 + fVar13) * fVar15;
              local_18 = local_18 + 4;
            } while (uVar23 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1060));
          }
          (**(code **)(**(int **)((int)param_1 + 4) + 8))(local_10,0,local_14);
          local_10 = local_10 + 1;
        } while (local_10 < *(uint *)(*(int *)((int)param_1 + 4) + 0x1064));
      }
      OID__FreeObject_Callback(local_8);
      iVar16 = 0;
    }
    OID__FreeObject_Callback(local_14);
  }
  return iVar16;
}
