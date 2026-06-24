/* address: 0x0052aaf0 */
/* name: CD3DApplication__MsgProc */
/* signature: int __thiscall CD3DApplication__MsgProc(void * this, void * hwnd, uint msg, uint wparam, int lparam) */


int __thiscall CD3DApplication__MsgProc(void *this,void *hwnd,uint msg,uint wparam,int lparam)

{
  LPRECT lpRect;
  int iVar1;
  int iVar2;
  int iVar3;
  LRESULT LVar4;
  tagPOINT local_10 [2];

  if (0x112 < msg) {
    switch(msg) {
    case 0x200:
      if (((*(int *)((int)this + 0x32e48) != 0) && (*(int *)((int)this + 0x32e4c) != 0)) &&
         (*(int *)((int)this + 0x32ea0) != 0)) {
        GetCursorPos(local_10);
        ScreenToClient(*(HWND *)((int)this + 0x32e94),local_10);
        (**(code **)(**(int **)((int)this + 0x32ea0) + 0x2c))
                  (*(int **)((int)this + 0x32ea0),local_10[0].x,local_10[0].y,0);
      }
      break;
    case 0x211:
      (**(code **)(*(int *)this + 0x34))(1);
      break;
    case 0x212:
      (**(code **)(*(int *)this + 0x34))(0);
      break;
    case 0x218:
      if (wparam == 0) {
        return 1;
      }
      if (wparam == 7) {
        return 1;
      }
      break;
    case 0x231:
      if (*(int *)((int)this + 0x32e50) != 0) {
        CD3DApplication__Helper_0052cd20(2);
      }
      break;
    case 0x232:
      if (*(int *)((int)this + 0x32e50) != 0) {
        CD3DApplication__Helper_0052cd20(1);
      }
      if ((*(int *)((int)this + 0x32e48) != 0) && (*(int *)((int)this + 0x32e44) != 0)) {
        lpRect = (LPRECT)((int)this + 0x3300c);
        local_10[0].x = lpRect->left;
        local_10[0].y = *(int *)((int)this + 0x33010);
        iVar3 = *(int *)((int)this + 0x33014);
        iVar1 = *(int *)((int)this + 0x33018);
        GetWindowRect(*(HWND *)((int)this + 0x32e94),(LPRECT)((int)this + 0x32ffc));
        GetClientRect(*(HWND *)((int)this + 0x32e94),lpRect);
        iVar2 = *(int *)((int)this + 0x33014) - lpRect->left;
        if ((iVar3 - local_10[0].x != iVar2) ||
           (iVar1 - local_10[0].y != *(int *)((int)this + 0x33018) - *(int *)((int)this + 0x33010)))
        {
          *(undefined4 *)((int)this + 0x32e4c) = 0;
          *(int *)((int)this + 0x32e58) = iVar2;
          *(int *)((int)this + 0x32e5c) =
               *(int *)((int)this + 0x33018) - *(int *)((int)this + 0x33010);
          iVar3 = CD3DApplication__Unk_0052b760(this);
          if (iVar3 < 0) {
            CD3DApplication__Unk_0052c4f0(-0x7dfffff4);
            return 0;
          }
          *(undefined4 *)((int)this + 0x32e4c) = 1;
        }
      }
    }
    goto switchD_0052ac8c_caseD_201;
  }
  if (msg == 0x112) {
    if (wparam < 0xf031) {
      if ((wparam != 0xf030) && ((wparam != 0xf000 && (wparam != 0xf010))))
      goto switchD_0052ac8c_caseD_201;
    }
    else if ((wparam != 0xf100) && (wparam != 0xf170)) goto switchD_0052ac8c_caseD_201;
  }
  else {
    if (msg < 0x25) {
      if (msg == 0x24) {
        *(undefined4 *)(lparam + 0x18) = 100;
        *(undefined4 *)(lparam + 0x1c) = 100;
      }
      else if (msg == 5) {
        if ((wparam == 4) || (wparam == 1)) {
          *(undefined4 *)((int)this + 0x32e48) = 0;
        }
        else {
          *(undefined4 *)((int)this + 0x32e48) = 1;
        }
      }
      else {
        if (msg == 0x10) {
          CEngine__MarkDeviceResetPending();
          return 0;
        }
        if ((((msg == 0x20) && (*(int *)((int)this + 0x32e48) != 0)) &&
            (*(int *)((int)this + 0x32e4c) != 0)) && (*(int *)((int)this + 0x32e44) == 0)) {
          SetCursor((HCURSOR)0x0);
          if (*(int *)((int)this + 0x330c4) != 0) {
            (**(code **)(**(int **)((int)this + 0x32ea0) + 0x30))(*(int **)((int)this + 0x32ea0),1);
          }
          return 1;
        }
      }
      goto switchD_0052ac8c_caseD_201;
    }
    if (msg != 0x84) {
      if (msg == 0x111) {
        if ((wparam & 0xffff) == 0x9c42) {
          return 0;
        }
        if ((wparam & 0xffff) == 0x9c46) {
          SendMessageA(hwnd,0x10,0,0);
          return 0;
        }
      }
      goto switchD_0052ac8c_caseD_201;
    }
  }
  if (*(int *)((int)this + 0x32e44) == 0) {
    return 1;
  }
switchD_0052ac8c_caseD_201:
  LVar4 = DefWindowProcA(hwnd,msg,wparam,lparam);
  return LVar4;
}
