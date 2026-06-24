/* address: 0x0052af00 */
/* name: CD3DApplication__Initialize3DEnvironment */
/* signature: undefined CD3DApplication__Initialize3DEnvironment(void) */


/* WARNING: Removing unreachable block (ram,0x0052afb1) */
/* WARNING: Removing unreachable block (ram,0x0052afdd) */
/* WARNING: Removing unreachable block (ram,0x0052afe3) */
/* WARNING: Removing unreachable block (ram,0x0052afee) */
/* WARNING: Removing unreachable block (ram,0x0052aff9) */
/* WARNING: Removing unreachable block (ram,0x0052b004) */
/* WARNING: Removing unreachable block (ram,0x0052b009) */
/* WARNING: Removing unreachable block (ram,0x0052b00e) */
/* WARNING: Removing unreachable block (ram,0x0052b016) */
/* WARNING: Removing unreachable block (ram,0x0052b01a) */
/* WARNING: Removing unreachable block (ram,0x0052b027) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CD3DApplication__Initialize3DEnvironment(int *param_1,char param_2)

{
  int *piVar1;
  char cVar2;
  float fVar3;
  int *piVar4;
  int iVar5;
  LPCSTR pCVar6;
  DWORD DVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  char *pcVar12;
  CHAR *pCVar13;
  int *piVar14;
  int *piVar15;
  undefined **lpString2;
  char *pcVar16;
  undefined4 uStack_ac;
  int local_a8;
  char acStack_84 [132];

  CVar__SetValueRounded(0xbf800000);
  CVar__SetValueRounded(0xbf800000);
  if (DAT_00662f39 == '\0') {
    pcVar16 = s_cardid_txt_0064c384;
  }
  else {
    pcVar16 = s_c__cardid_txt_0064c390;
  }
  CD3DApplication__Helper_005286e0(pcVar16);
  uStack_ac = CONCAT13(DAT_0089c05c != 0,(undefined3)uStack_ac);
LAB_0052af5b:
  do {
    iVar5 = param_1[0xcb90];
    piVar1 = param_1 + iVar5 * 0x145b + param_1[iVar5 * 0x145b + 0x145b] * 0x3da + 0x119;
    piVar15 = piVar1 + piVar1[0x3d4] * 6 + 0x50;
    (**(code **)*param_1)();
    piVar4 = param_1 + 0xcb96;
    piVar14 = piVar4;
    for (iVar8 = 0xe; iVar8 != 0; iVar8 = iVar8 + -1) {
      *piVar14 = 0;
      piVar14 = piVar14 + 1;
    }
    param_1[0xcb9e] = param_1[0xcb91];
    param_1[0xcb99] = DAT_00662db8;
    iVar8 = piVar1[0x3d6];
    if (piVar1[0x3d6] == -1) {
      iVar8 = DAT_0089c08c;
    }
    param_1[0xcb9a] = iVar8;
    param_1[0xcb9f] = param_1[0xcc2c];
    param_1[0xcb9c] = 1;
    param_1[0xcba0] = piVar15[5];
    param_1[0xcb9d] = param_1[0xcba5];
    if (DAT_0089c09c != 0) {
      param_1[0xcb9c] = 3;
      param_1[0xcb9a] = 0;
    }
    if (param_1[0xcb91] == 0) {
      if ((g_TryLockableBackbuffer != 0) || (iVar5 = -0x80000000, DAT_0089c07c != 0)) {
        iVar5 = 1;
      }
      param_1[0xcba3] = iVar5;
      *piVar4 = *piVar15;
      param_1[0xcb97] = piVar15[1];
      param_1[0xcb98] = piVar15[2];
    }
    else {
      param_1[0xcba3] = 0;
      *piVar4 = param_1[0xcc05] - param_1[0xcc03];
      uVar9 = 0;
      param_1[0xcb97] = param_1[0xcc06] - param_1[0xcc04];
      iVar8 = param_1[iVar5 * 0x145b + 0x117];
      param_1[0xcb98] = iVar8;
      if (piVar1[0x4f] != 0) {
        piVar4 = piVar1 + 0x55;
        do {
          if (((piVar4[-3] == iVar8) &&
              (param_1[0xcba0] = *piVar4, piVar4[-5] == param_1[iVar5 * 0x145b + 0x114])) &&
             (piVar4[-4] == param_1[iVar5 * 0x145b + 0x115])) break;
          uVar9 = uVar9 + 1;
          piVar4 = piVar4 + 6;
        } while (uVar9 < (uint)piVar1[0x4f]);
      }
    }
    fVar3 = _DAT_005e4aec;
    if ((g_ScreenShape == 1) || (fVar3 = _DAT_005e4af0, g_ScreenShape != 2)) {
      param_1[0xcba4] = (int)(((float)(uint)param_1[0xcb97] / (float)param_1[0xcb96]) * fVar3);
    }
    else {
      param_1[0xcba4] = 0x3f800000;
    }
    if ((uStack_ac._3_1_ != '\0') && (param_1[0xcb9a] == 0)) {
      param_1[0xcba1] = param_1[0xcba1] | 1;
    }
    CConsole__Printf(&DAT_0066eb90,s_Creating_device____0064c35c);
    uVar9 = 0;
    pcVar16 = acStack_84;
    do {
      sprintf(pcVar16,&DAT_0063e3dc);
      pcVar12 = pcVar16 + 2;
      if (((byte)uVar9 & 3) == 3) {
        *pcVar12 = ' ';
        pcVar12 = pcVar16 + 3;
      }
      uVar9 = uVar9 + 1;
      pcVar16 = pcVar12;
    } while (uVar9 < 0x38);
    *pcVar12 = '\0';
    CConsole__Printf(&DAT_0066eb90,&DAT_006245d8);
    uVar9 = 0;
    if (DAT_0089c04c != (int *)0x0) {
      (**(code **)(*DAT_0089c04c + 8))(DAT_0089c04c);
      DAT_0089c04c = (int *)0x0;
    }
    if ((param_2 == '\0') || (piVar4 = (int *)param_1[0xcba8], piVar4 == (int *)0x0)) {
      iVar5 = (**(code **)(*(int *)param_1[0xcba7] + 0x40))
                        ((int *)param_1[0xcba7],param_1[0xcb90],*piVar1,param_1[0xcba6],
                         -(uint)(DAT_00662f3d != '\0') & 0x100 | piVar15[3],param_1 + 0xcb96,
                         param_1 + 0xcba8);
    }
    else {
      iVar5 = (**(code **)(*piVar4 + 0x40))(piVar4,param_1 + 0xcb96);
    }
    if (-1 < iVar5) {
      if (DAT_00662f3d != '\0') {
        (**(code **)(*(int *)param_1[0xcba8] + 0x1d8))((int *)param_1[0xcba8],5,&DAT_0089c04c);
      }
      CConsole__Printf(&DAT_0066eb90,s_Succeeded__0064c2bc);
      (**(code **)(*(int *)param_1[0xcba8] + 0x10))((int *)param_1[0xcba8]);
      CConsole__Printf(&DAT_0066eb90,s_Available_texture_memory___d_Mb_0064c29c);
      if (param_1[0xcb91] != 0) {
        SetWindowPos((HWND)param_1[0xcba5],(HWND)0xfffffffe,param_1[0xcbff],param_1[0xcc00],
                     param_1[0xcc01] - param_1[0xcbff],param_1[0xcc02] - param_1[0xcc00],0x40);
      }
      piVar4 = (int *)param_1[0xcba8];
      (**(code **)(*piVar4 + 0x1c))(piVar4,param_1 + 0xcba9);
      param_1[0xcbfd] = *(int *)(uStack_ac + 0xc);
      iVar8 = *piVar1;
      if (iVar8 == 2) {
        lpString2 = &PTR_LAB_0064c1e8;
LAB_0052b4ee:
        lstrcpyA((LPSTR)(param_1 + 0xcc0a),(LPCSTR)lpString2);
      }
      else {
        if (iVar8 == 1) {
          lpString2 = &PTR_LAB_0064c1ec;
          goto LAB_0052b4ee;
        }
        if (iVar8 == 3) {
          lpString2 = (undefined **)&DAT_0064c08c;
          goto LAB_0052b4ee;
        }
      }
      uVar9 = *(uint *)(uStack_ac + 0xc);
      if (((uVar9 & 0x40) == 0) || ((uVar9 & 0x10) == 0)) {
        if ((uVar9 & 0x40) != 0) {
          if (*piVar1 == 1) {
            pcVar16 = s__hw_vp__0064c268;
          }
          else {
            pcVar16 = s__simulated_hw_vp__0064c254;
          }
          goto LAB_0052b575;
        }
        if ((uVar9 & 0x80) != 0) {
          if (*piVar1 == 1) {
            pcVar16 = s__mixed_vp__0064c248;
          }
          else {
            pcVar16 = s__simulated_mixed_vp__0064c230;
          }
          goto LAB_0052b575;
        }
        if ((uVar9 & 0x20) != 0) {
          pcVar16 = s__sw_vp__0064c224;
          goto LAB_0052b575;
        }
      }
      else {
        if (*piVar1 == 1) {
          pcVar16 = s__pure_hw_vp__0064c28c;
        }
        else {
          pcVar16 = s__simulated_pure_hw_vp__0064c274;
        }
LAB_0052b575:
        lstrcatA((LPSTR)(param_1 + 0xcc0a),pcVar16);
      }
      if (*piVar1 == 1) {
        lstrcatA((LPSTR)(param_1 + 0xcc0a),&DAT_006291c4);
        pCVar6 = (LPCSTR)CD3DApplication__Helper_004f7c70((void *)(iVar5 + 0x200));
        lstrcatA((LPSTR)(param_1 + 0xcc0a),pCVar6);
      }
      pcVar16 = (char *)CD3DApplication__Helper_004f7c70(&DAT_00622d9c);
      uVar9 = 0xffffffff;
      break;
    }
    if (iVar5 != -0x7789f798) {
      HResultToString();
      CConsole__Printf(&DAT_0066eb90,s_Failed_for__s__0064c334);
      if (uStack_ac._3_1_ != '\0') {
        CConsole__Printf(&DAT_0066eb90,s_Falling_back_to_no_lockable_back_0064c30c);
        uStack_ac = uStack_ac & 0xffffff;
        goto LAB_0052af5b;
      }
      if (param_1[0xcb9a] != 0) {
        CConsole__Printf(&DAT_0066eb90,s_Falling_back_to_no_multisampling_0064c2e8);
        CDXEngine__Helper_004d1710(0xe5);
        piVar1[0x3d6] = 0;
        goto LAB_0052af5b;
      }
      uVar10 = piVar1[0x3d4];
      uVar11 = 0;
      if (piVar1[0x4f] != 0) {
        piVar4 = piVar1 + 0x52;
        do {
          if (((piVar4[-2] == param_1[0xcc2f]) && (piVar4[-1] == param_1[0xcc30])) &&
             ((iVar5 = *piVar4, uVar9 = uVar11, iVar5 == 0x14 ||
              ((iVar5 == 0x15 || (iVar5 == 0x16)))))) break;
          uVar11 = uVar11 + 1;
          piVar4 = piVar4 + 6;
        } while (uVar11 < (uint)piVar1[0x4f]);
      }
      piVar1[0x3d4] = uVar9;
      if (uVar9 != uVar10) {
        CConsole__Printf(&DAT_0066eb90,s_Falling_back_to_a_friendly_mode_0064c2c8);
        CDXEngine__Helper_004d1710(0xe6);
        uStack_ac = CONCAT13(1,(undefined3)uStack_ac);
        goto LAB_0052af5b;
      }
      goto LAB_0052b6be;
    }
    CConsole__Printf(&DAT_0066eb90,s_Failed_for_device_lost__0064c344);
    Sleep(100);
  } while( true );
  while( true ) {
    uVar9 = uVar9 - 1;
    pcVar12 = pcVar16 + 1;
    cVar2 = *pcVar16;
    pcVar16 = pcVar12;
    if (cVar2 == '\0') break;
    pcVar12 = pcVar16;
    if (uVar9 == 0) break;
  }
  uVar9 = ~uVar9;
  iVar5 = -1;
  piVar15 = param_1 + 0xcc0a;
  do {
    piVar14 = piVar15;
    if (iVar5 == 0) break;
    iVar5 = iVar5 + -1;
    piVar14 = (int *)((int)piVar15 + 1);
    iVar8 = *piVar15;
    piVar15 = piVar14;
  } while ((char)iVar8 != '\0');
  pCVar13 = pcVar12 + -uVar9;
  pCVar6 = (LPCSTR)((int)piVar14 + -1);
  for (uVar10 = uVar9 >> 2; uVar10 != 0; uVar10 = uVar10 - 1) {
    *(undefined4 *)pCVar6 = *(undefined4 *)pCVar13;
    pCVar13 = pCVar13 + 4;
    pCVar6 = pCVar6 + 4;
  }
  for (uVar9 = uVar9 & 3; uVar9 != 0; uVar9 = uVar9 - 1) {
    *pCVar6 = *pCVar13;
    pCVar13 = pCVar13 + 1;
    pCVar6 = pCVar6 + 1;
  }
  OutputDebugStringA((LPCSTR)(param_1 + 0xcc0a));
  piVar15 = (int *)0x0;
  (**(code **)(*(int *)param_1[0xcba8] + 0x48))((int *)param_1[0xcba8],0,0,0,&stack0xffffff50);
  (**(code **)(*piVar4 + 0x30))(piVar4,param_1 + 0xcbf5);
  (**(code **)(*piVar15 + 8))(piVar15);
  if ((param_1[0xcc31] != 0) && (param_1[0xcb91] == 0)) {
    DVar7 = GetClassLongA((HWND)param_1[0xcba5],-0xc);
    CD3DApplication__Unk_0052c8d0((void *)param_1[0xcba8],DVar7);
    (**(code **)(*(int *)param_1[0xcba8] + 0x30))((int *)param_1[0xcba8],1);
  }
  local_a8 = (**(code **)(*param_1 + 0x20))();
  if (-1 < local_a8) {
    param_1[0xcb92] = 1;
    CConsole__Printf(&DAT_0066eb90,s_D3DA__I3DE_OK_0064c214);
    return 0;
  }
  (**(code **)(*param_1 + 0x14))();
  (**(code **)(*param_1 + 0x18))();
  piVar4 = (int *)param_1[0xcba8];
  if (piVar4 != (int *)0x0) {
    (**(code **)(*piVar4 + 8))(piVar4);
    param_1[0xcba8] = 0;
  }
LAB_0052b6be:
  if (*piVar1 == 1) {
    CD3DApplication__Unk_0052c4f0(local_a8);
    param_1[0xcb90] = 0;
    uVar9 = 0;
    if (param_1[0x118] != 0) {
      piVar4 = param_1 + 0x119;
      do {
        if (*piVar4 == 2) {
          param_1[0x145b] = uVar9;
          param_1[0xcb91] = param_1[uVar9 * 0x3da + 0x4ee];
          break;
        }
        uVar9 = uVar9 + 1;
        piVar4 = piVar4 + 0x3da;
      } while (uVar9 < (uint)param_1[0x118]);
    }
    if (param_1[param_1[0x145b] * 0x3da + 0x119] == 2) {
      local_a8 = CD3DApplication__Initialize3DEnvironment(0);
    }
  }
  return local_a8;
}
