/* address: 0x0052bc80 */
/* name: CD3DApplication__Unk_0052bc80 */
/* signature: int __stdcall CD3DApplication__Unk_0052bc80(int param_1, void * param_2, int param_3, int param_4) */


int CD3DApplication__Unk_0052bc80(int param_1,void *param_2,int param_3,int param_4)

{
  undefined4 *puVar1;
  HWND hWnd;
  HWND hWnd_00;
  HWND hWnd_01;
  HWND hWnd_02;
  HWND hWnd_03;
  HWND hWnd_04;
  int iVar2;
  WPARAM WVar3;
  char *format;
  undefined4 uVar4;
  int iVar5;
  LPCSTR pCVar6;
  LRESULT LVar7;
  short sVar8;
  uint lParam;
  uint uVar9;
  char local_50 [80];

  hWnd = GetDlgItem((HWND)param_1,0x3ea);
  hWnd_00 = GetDlgItem((HWND)param_1,1000);
  hWnd_01 = GetDlgItem((HWND)param_1,0x3eb);
  hWnd_02 = GetDlgItem((HWND)param_1,0x3f8);
  hWnd_03 = GetDlgItem((HWND)param_1,0x3fa);
  hWnd_04 = GetDlgItem((HWND)param_1,0x3ed);
  if (param_2 == (void *)0x110) {
    DAT_0089c048 = param_4;
    DAT_0089c030 = *(uint *)(param_4 + 0x32e40);
    iVar2 = param_4 + 4 + DAT_0089c030 * 0x516c;
    DAT_0089c02c = *(uint *)(iVar2 + 0x5168);
    iVar2 = iVar2 + 0x460 + DAT_0089c02c * 0xf68;
    DAT_0089c028 = *(void **)(iVar2 + 0xf50);
    DAT_0089c024 = *(int *)(iVar2 + 0xf54);
    DAT_0089c020 = *(uint *)(iVar2 + 0xf58);
    DAT_0089c034 = DAT_0089c020;
    DAT_0089c038 = DAT_0089c024;
    DAT_0089c03c = DAT_0089c028;
    DAT_0089c040 = DAT_0089c02c;
    DAT_0089c044 = DAT_0089c030;
  }
  else {
    if (param_2 != (void *)0x111) {
      return 0;
    }
    DAT_0089c024 = SendMessageA(hWnd_02,0xf0,0,0);
    sVar8 = (short)param_3;
    if (sVar8 == 1) {
      if ((((DAT_0089c030 == DAT_0089c044) && (DAT_0089c02c == DAT_0089c040)) &&
          (DAT_0089c028 == DAT_0089c03c)) &&
         ((DAT_0089c024 == DAT_0089c038 && (DAT_0089c020 == DAT_0089c034)))) {
        EndDialog((HWND)param_1,2);
        return 1;
      }
      *(uint *)(DAT_0089c048 + 0x32e40) = DAT_0089c030;
      iVar2 = DAT_0089c048 + 4 + DAT_0089c030 * 0x516c;
      *(uint *)(iVar2 + 0x5168) = DAT_0089c02c;
      *(void **)(iVar2 + 0x13b0 + DAT_0089c02c * 0xf68) = DAT_0089c028;
      *(int *)(iVar2 + 0x13b4 + DAT_0089c02c * 0xf68) = DAT_0089c024;
      *(uint *)(iVar2 + 0x13b8 + DAT_0089c02c * 0xf68) = DAT_0089c020;
      EndDialog((HWND)param_1,1);
      return 1;
    }
    if (sVar8 == 2) {
      EndDialog((HWND)param_1,2);
      return 1;
    }
    if ((short)((uint)param_3 >> 0x10) == 9) {
      if (sVar8 == 0x3ea) {
        DAT_0089c030 = SendMessageA(hWnd,0x147,0,0);
        DAT_0089c02c = *(uint *)(DAT_0089c048 + 0x516c + DAT_0089c030 * 0x516c);
        iVar2 = DAT_0089c048 + 4 + DAT_0089c030 * 0x516c + DAT_0089c02c * 0xf68;
      }
      else {
        if (sVar8 != 1000) {
          if (sVar8 == 0x3eb) {
            DAT_0089c028 = (void *)SendMessageA(hWnd_01,0x147,0,0);
          }
          else if (sVar8 == 0x3ed) {
            WVar3 = SendMessageA(hWnd_04,0x147,0,0);
            DAT_0089c020 = SendMessageA(hWnd_04,0x150,WVar3,0);
          }
          goto LAB_0052bfdf;
        }
        iVar2 = DAT_0089c048 + 4;
        iVar5 = DAT_0089c030 * 0x516c;
        DAT_0089c02c = SendMessageA(hWnd_00,0x147,0,0);
        iVar2 = iVar2 + iVar5 + DAT_0089c02c * 0xf68;
      }
      DAT_0089c028 = *(void **)(iVar2 + 0x13b0);
      DAT_0089c024 = *(int *)(iVar2 + 0x13b4);
    }
  }
LAB_0052bfdf:
  SendMessageA(hWnd,0x14b,0,0);
  SendMessageA(hWnd_00,0x14b,0,0);
  SendMessageA(hWnd_01,0x14b,0,0);
  SendMessageA(hWnd_04,0x14b,0,0);
  iVar2 = DAT_0089c048 + 4 + DAT_0089c030 * 0x516c;
  puVar1 = (undefined4 *)(iVar2 + 0x460 + DAT_0089c02c * 0xf68);
  uVar9 = 0;
  if (*(int *)(DAT_0089c048 + 0x32e3c) != 0) {
    param_2 = (void *)0x0;
    do {
      WVar3 = SendMessageA(hWnd,0x143,0,(int)param_2 + DAT_0089c048 + 0x204);
      SendMessageA(hWnd,0x151,WVar3,uVar9);
      if (uVar9 == DAT_0089c030) {
        SendMessageA(hWnd,0x14e,WVar3,0);
      }
      uVar9 = uVar9 + 1;
      param_2 = (void *)((int)param_2 + 0x516c);
    } while (uVar9 < *(uint *)(DAT_0089c048 + 0x32e3c));
  }
  uVar9 = 0;
  if (*(int *)(iVar2 + 0x45c) != 0) {
    param_2 = (void *)(iVar2 + 0x594);
    do {
      WVar3 = SendMessageA(hWnd_00,0x143,0,*(LPARAM *)param_2);
      SendMessageA(hWnd_00,0x151,WVar3,uVar9);
      if (uVar9 == DAT_0089c02c) {
        SendMessageA(hWnd_00,0x14e,WVar3,0);
      }
      uVar9 = uVar9 + 1;
      param_2 = (void *)((int)param_2 + 0xf68);
    } while (uVar9 < *(uint *)(iVar2 + 0x45c));
  }
  param_2 = (void *)0x0;
  if (puVar1[0x4f] != 0) {
    do {
      format = (char *)CD3DApplication__Helper_004f7c70(s__ld_x__ld_x__ld_0064c3b4);
      sprintf(local_50,format);
      WVar3 = SendMessageA(hWnd_01,0x143,0,(LPARAM)local_50);
      SendMessageA(hWnd_01,0x151,WVar3,(LPARAM)param_2);
      if (param_2 == DAT_0089c028) {
        SendMessageA(hWnd_01,0x14e,WVar3,0);
      }
      param_2 = (void *)((int)param_2 + 1);
    } while (param_2 < (void *)puVar1[0x4f]);
  }
  lParam = 0;
  uVar9 = DAT_0089c030;
  iVar2 = DAT_0089c048;
  do {
    if (DAT_0089c024 == 0) {
      uVar4 = puVar1[(int)DAT_0089c028 * 6 + 0x52];
    }
    else {
      uVar4 = *(undefined4 *)(iVar2 + 0x45c + uVar9 * 0x516c);
    }
    if ((lParam != 1) &&
       (iVar5 = (**(code **)(**(int **)(iVar2 + 0x32e9c) + 0x2c))
                          (*(int **)(iVar2 + 0x32e9c),uVar9,*puVar1,uVar4,DAT_0089c024,lParam,0),
       uVar9 = DAT_0089c030, iVar2 = DAT_0089c048, -1 < iVar5)) {
      if (lParam == 0) {
        pCVar6 = (LPCSTR)CD3DApplication__Helper_004f7c70(&DAT_0064c3ac);
        lstrcpyA(local_50,pCVar6);
      }
      else {
        uVar9 = lParam;
        pCVar6 = (LPCSTR)CD3DApplication__Helper_004f7c70(s__d_samples_0064c3a0);
        wsprintfA(local_50,pCVar6,uVar9);
      }
      WVar3 = SendMessageA(hWnd_04,0x143,0,(LPARAM)local_50);
      SendMessageA(hWnd_04,0x151,WVar3,lParam);
      if ((lParam == DAT_0089c020) || (uVar9 = DAT_0089c030, iVar2 = DAT_0089c048, lParam == 0)) {
        SendMessageA(hWnd_04,0x14e,WVar3,0);
        uVar9 = DAT_0089c030;
        iVar2 = DAT_0089c048;
      }
    }
    lParam = lParam + 1;
  } while (lParam < 0x11);
  WVar3 = SendMessageA(hWnd_04,0x147,0,0);
  DAT_0089c020 = SendMessageA(hWnd_04,0x150,WVar3,0);
  LVar7 = SendMessageA(hWnd_04,0x146,0,0);
  EnableWindow(hWnd_04,(uint)(1 < LVar7));
  EnableWindow(hWnd_02,puVar1[0x4e]);
  if (DAT_0089c024 == 0) {
    SendMessageA(hWnd_02,0xf1,0,0);
    SendMessageA(hWnd_03,0xf1,1,0);
    EnableWindow(hWnd_01,1);
    return 1;
  }
  SendMessageA(hWnd_02,0xf1,1,0);
  SendMessageA(hWnd_03,0xf1,0,0);
  EnableWindow(hWnd_01,0);
  return 1;
}
