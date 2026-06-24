/* address: 0x0052c8d0 */
/* name: CD3DApplication__Unk_0052c8d0 */
/* signature: int __cdecl CD3DApplication__Unk_0052c8d0(void * param_1, int param_2) */


int __cdecl CD3DApplication__Unk_0052c8d0(void *param_1,int param_2)

{
  BOOL BVar1;
  int iVar2;
  HDC pHVar3;
  int iVar4;
  int *piVar5;
  int *cLines;
  uint uVar6;
  int unaff_EBX;
  int *unaff_ESI;
  int unaff_EDI;
  int iVar7;
  tagBITMAPINFO *ptVar8;
  int iVar9;
  void *local_8c;
  int *local_88;
  HGDIOBJ pvStack_84;
  LPVOID local_80;
  HDC local_7c;
  int iStack_78;
  uint uStack_74;
  ICONINFO local_70;
  HDC local_5c;
  HDC local_58;
  undefined1 auStack_4c [8];
  tagBITMAPINFO tStack_44;
  undefined1 auStack_18 [4];
  int iStack_14;
  int *piStack_10;

  local_88 = (int *)0x0;
  local_58 = (HDC)0x0;
  local_7c = (HDC)0x0;
  local_5c = (HDC)0x0;
  local_80 = (LPVOID)0x0;
  local_8c = (void *)0x0;
  local_70.fIcon = 0;
  local_70.xHotspot = 0;
  local_70.yHotspot = 0;
  local_70.hbmMask = (HBITMAP)0x0;
  iVar7 = -0x7fffbffb;
  local_70.hbmColor = (HBITMAP)0x0;
  BVar1 = GetIconInfo((HICON)param_2,&local_70);
  if ((BVar1 != 0) &&
     (iVar2 = GetObjectA(local_70.hbmMask,0x18,auStack_18), piVar5 = piStack_10, iVar2 != 0)) {
    iStack_78 = iStack_14;
    cLines = piStack_10;
    if (local_70.hbmColor == (HBITMAP)0x0) {
      cLines = (int *)((uint)piStack_10 >> 1);
    }
    uStack_74 = (uint)(local_70.hbmColor == (HBITMAP)0x0);
    iVar7 = (**(code **)(*(int *)param_1 + 0x90))(param_1,iStack_14,cLines,0x15,3,&local_88,0);
    if (-1 < iVar7) {
      local_8c = (void *)OID__AllocObject((int)piVar5 * iStack_14 * 4,0,&DAT_00662b2c,0);
      ptVar8 = &tStack_44;
      for (iVar7 = 0xb; iVar7 != 0; iVar7 = iVar7 + -1) {
        (ptVar8->bmiHeader).biSize = 0;
        ptVar8 = (tagBITMAPINFO *)&(ptVar8->bmiHeader).biWidth;
      }
      tStack_44.bmiHeader.biSize = 0x28;
      tStack_44.bmiHeader.biWidth = iStack_14;
      tStack_44.bmiHeader.biHeight = (LONG)piVar5;
      tStack_44.bmiHeader.biPlanes = 1;
      tStack_44.bmiHeader.biBitCount = 0x20;
      tStack_44.bmiHeader.biCompression = 0;
      local_5c = GetDC((HWND)0x0);
      local_7c = CreateCompatibleDC(local_5c);
      if (local_7c == (HDC)0x0) {
        iVar7 = -0x7fffbffb;
      }
      else {
        pvStack_84 = SelectObject(local_7c,local_70.hbmMask);
        GetDIBits(local_7c,local_70.hbmMask,0,(UINT)piVar5,local_8c,&tStack_44,0);
        SelectObject(local_7c,pvStack_84);
        if (uStack_74 == 0) {
          local_80 = (LPVOID)OID__AllocObject((int)cLines * iStack_14 * 4,0,&DAT_00662b2c,0);
          pHVar3 = GetDC((HWND)0x0);
          pHVar3 = CreateCompatibleDC(pHVar3);
          local_58 = pHVar3;
          if (pHVar3 == (HDC)0x0) {
            iVar7 = -0x7fffbffb;
            goto LAB_0052cb9f;
          }
          SelectObject(pHVar3,local_70.hbmColor);
          GetDIBits(pHVar3,local_70.hbmColor,0,(UINT)cLines,local_80,&tStack_44,0);
        }
        (**(code **)(*local_88 + 0x34))(local_88,auStack_4c,0,0);
        local_70.hbmMask = (HBITMAP)local_58;
        if (cLines != (int *)0x0) {
          iVar9 = 0;
          iVar2 = ((int)cLines + -1) * (int)local_88;
          iVar7 = ((int)piVar5 + -1) * (int)local_88;
          local_70.hbmColor = (HBITMAP)-(int)local_88;
          do {
            piVar5 = (int *)0x0;
            if (local_88 != (int *)0x0) {
              do {
                if (pvStack_84 == (HGDIOBJ)0x0) {
                  iVar4 = (iVar2 + (int)piVar5) * 4;
                  uVar6 = *(uint *)(iVar4 + unaff_EBX);
                  iVar4 = *(int *)(iVar4 + unaff_EDI);
                }
                else {
                  uVar6 = *(uint *)(unaff_EDI + (iVar2 + (int)piVar5) * 4);
                  iVar4 = *(int *)(unaff_EDI + ((int)piVar5 + iVar7) * 4);
                }
                if (iVar4 == 0) {
                  local_58[iVar9 + (int)piVar5].unused = uVar6 | 0xff000000;
                }
                else {
                  local_58[iVar9 + (int)piVar5].unused = 0;
                }
                piVar5 = (int *)((int)piVar5 + 1);
              } while (piVar5 < local_88);
            }
            iVar7 = (int)&(local_70.hbmColor)->unused + iVar7;
            iVar2 = (int)&(local_70.hbmColor)->unused + iVar2;
            iVar9 = iVar9 + (int)local_88;
            cLines = (int *)((int)cLines + -1);
          } while (cLines != (int *)0x0);
        }
        (**(code **)(*unaff_ESI + 0x38))(unaff_ESI);
        iVar7 = (**(code **)(*piStack_10 + 0x28))(piStack_10,local_80,local_7c,unaff_EDI);
        if (-1 < iVar7) {
          iVar7 = 0;
        }
      }
    }
  }
LAB_0052cb9f:
  if (local_70.hbmMask != (HBITMAP)0x0) {
    DeleteObject(local_70.hbmMask);
  }
  if (local_70.hbmColor != (HBITMAP)0x0) {
    DeleteObject(local_70.hbmColor);
  }
  if (local_5c != (HDC)0x0) {
    ReleaseDC((HWND)0x0,local_5c);
  }
  if (local_58 != (HDC)0x0) {
    DeleteDC(local_58);
  }
  if (local_7c != (HDC)0x0) {
    DeleteDC(local_7c);
  }
  if (local_80 != (void *)0x0) {
    OID__FreeObject(local_80);
  }
  if (local_8c != (void *)0x0) {
    OID__FreeObject(local_8c);
  }
  if (local_88 != (int *)0x0) {
    (**(code **)(*local_88 + 8))(local_88);
  }
  return iVar7;
}
