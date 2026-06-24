/* address: 0x00564c09 */
/* name: CRT__OpenFileByModeString */
/* signature: int __cdecl CRT__OpenFileByModeString(int param_1, void * param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CRT__OpenFileByModeString(int param_1,void *param_2,int param_3,void *param_4)

{
  char cVar1;
  bool bVar2;
  bool bVar3;
  bool bVar4;
  uint uVar5;
  uint uVar6;

  bVar4 = false;
  bVar3 = false;
  cVar1 = *(char *)param_2;
  if (cVar1 == 'a') {
    uVar5 = 0x109;
  }
  else {
    if (cVar1 == 'r') {
      uVar5 = 0;
      uVar6 = DAT_009d0ad4 | 1;
      goto LAB_00564c4a;
    }
    if (cVar1 != 'w') {
      return 0;
    }
    uVar5 = 0x301;
  }
  uVar6 = DAT_009d0ad4 | 2;
LAB_00564c4a:
  bVar2 = true;
LAB_00564c4d:
  cVar1 = *(char *)((int)param_2 + 1);
  param_2 = (void *)((int)param_2 + 1);
  if ((cVar1 == '\0') || (!bVar2)) {
    uVar5 = CRT__OpenFd(param_1,uVar5,param_3,0x1a4);
    if ((int)uVar5 < 0) {
      return 0;
    }
    _DAT_009d0908 = _DAT_009d0908 + 1;
    *(uint *)((int)param_4 + 0xc) = uVar6;
    *(undefined4 *)((int)param_4 + 4) = 0;
    *(undefined4 *)param_4 = 0;
    *(undefined4 *)((int)param_4 + 8) = 0;
    *(undefined4 *)((int)param_4 + 0x1c) = 0;
    *(uint *)((int)param_4 + 0x10) = uVar5;
    return (int)param_4;
  }
  if (cVar1 < 'U') {
    if (cVar1 == 'T') {
      if ((uVar5 & 0x1000) == 0) {
        uVar5 = uVar5 | 0x1000;
        goto LAB_00564c4d;
      }
    }
    else if (cVar1 == '+') {
      if ((uVar5 & 2) == 0) {
        uVar5 = uVar5 & 0xfffffffe | 2;
        uVar6 = uVar6 & 0xfffffffc | 0x80;
        goto LAB_00564c4d;
      }
    }
    else if (cVar1 == 'D') {
      if ((uVar5 & 0x40) == 0) {
        uVar5 = uVar5 | 0x40;
        goto LAB_00564c4d;
      }
    }
    else if (cVar1 == 'R') {
      if (!bVar3) {
        bVar3 = true;
        uVar5 = uVar5 | 0x10;
        goto LAB_00564c4d;
      }
    }
    else if ((cVar1 == 'S') && (!bVar3)) {
      bVar3 = true;
      uVar5 = uVar5 | 0x20;
      goto LAB_00564c4d;
    }
  }
  else {
    if (cVar1 == 'b') {
      if ((uVar5 & 0xc000) != 0) goto LAB_00564d2d;
      uVar5 = uVar5 | 0x8000;
      goto LAB_00564c4d;
    }
    if (cVar1 == 'c') {
      if (!bVar4) {
        bVar4 = true;
        uVar6 = uVar6 | 0x4000;
        goto LAB_00564c4d;
      }
    }
    else {
      if (cVar1 != 'n') {
        if ((cVar1 != 't') || ((uVar5 & 0xc000) != 0)) goto LAB_00564d2d;
        uVar5 = uVar5 | 0x4000;
        goto LAB_00564c4d;
      }
      if (!bVar4) {
        bVar4 = true;
        uVar6 = uVar6 & 0xffffbfff;
        goto LAB_00564c4d;
      }
    }
  }
LAB_00564d2d:
  bVar2 = false;
  goto LAB_00564c4d;
}
