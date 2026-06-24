/* address: 0x0057a934 */
/* name: CMeshCollisionVolume__Helper_0057a934 */
/* signature: int __thiscall CMeshCollisionVolume__Helper_0057a934(void * this, void * param_1, int param_2, int param_3) */


int __thiscall
CMeshCollisionVolume__Helper_0057a934(void *this,void *param_1,int param_2,int param_3)

{
  ushort uVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  LPCVOID lpBuffer;
  uint uVar6;
  undefined1 *puVar7;
  DWORD nNumberOfBytesToWrite;
  DWORD *pDVar8;
  undefined1 local_49c [1024];
  undefined2 local_9c;
  int local_9a;
  undefined2 uStack_96;
  undefined2 uStack_94;
  int local_92;
  DWORD local_8c;
  DWORD local_88 [3];
  undefined2 local_7c;
  ushort local_7a;
  undefined4 local_78;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  void *local_1c;
  undefined1 local_18;
  undefined1 local_17;
  undefined1 local_16;
  undefined1 local_15;
  undefined1 local_14 [4];
  uint local_10;
  LPCVOID local_c;
  undefined4 local_8;

  local_18 = 0;
  local_17 = 0;
  local_16 = 0;
  local_15 = 0;
  local_8 = 0;
  local_14[0] = 0;
  pDVar8 = local_88;
  for (iVar4 = 0x1b; iVar4 != 0; iVar4 = iVar4 + -1) {
    *pDVar8 = 0;
    pDVar8 = pDVar8 + 1;
  }
  iVar4 = *(int *)this;
  uVar6 = 0;
  local_8 = CONCAT13(0xff,CONCAT12(0xaa,CONCAT11(0x55,(undefined1)local_8)));
  local_14[1] = 0x24;
  local_14[2] = 0x49;
  local_14[3] = 0x6d;
  local_10 = 0xffdbb692;
  local_c = (LPCVOID)0x0;
  if (0x29 < iVar4) {
    if (iVar4 == 0x32) {
      local_88[0] = 0x28;
      local_78 = 0;
      local_7a = 8;
      local_c = (LPCVOID)0x400;
      uVar6 = 0;
      do {
        iVar4 = uVar6 * 4;
        local_49c[iVar4 + 3] = 0;
        uVar3 = (undefined1)uVar6;
        local_49c[iVar4 + 2] = uVar3;
        local_49c[iVar4 + 1] = uVar3;
        local_49c[iVar4] = uVar3;
        uVar6 = uVar6 + 1;
      } while (uVar6 < 0x100);
      goto LAB_0057ad1c;
    }
    if (iVar4 != 0x33) {
      if (iVar4 != 0x51) {
        return -0x7fffbffb;
      }
      local_88[0] = 0x34;
      local_78 = 3;
      local_7a = 0x10;
      local_60 = 0xffff;
      local_5c = 0xffff;
      local_58 = 0xffff;
      goto LAB_0057ad1c;
    }
    local_60 = 0xff;
    local_5c = 0xff;
    local_58 = 0xff;
LAB_0057ab3a:
    local_78 = 3;
    local_88[0] = 0x38;
    local_7a = 0x10;
    local_54 = 0xff00;
    goto LAB_0057ad1c;
  }
  if (iVar4 == 0x29) {
    iVar4 = *(int *)((int)this + 8);
    local_78 = 0;
    puVar7 = (undefined1 *)(iVar4 + 2);
    uVar6 = 0;
    local_88[0] = 0x28;
    local_7a = 8;
    local_c = (LPCVOID)0x400;
    do {
      iVar2 = uVar6 * 4;
      local_49c[iVar2 + 2] = *(undefined1 *)(iVar4 + iVar2);
      local_49c[iVar2 + 1] = puVar7[-1];
      uVar3 = *puVar7;
      local_49c[iVar2 + 3] = 0;
      uVar6 = uVar6 + 1;
      puVar7 = puVar7 + 4;
      local_49c[iVar2] = uVar3;
    } while (uVar6 < 0x100);
    goto LAB_0057ad1c;
  }
  switch(iVar4) {
  case 0x14:
    local_88[0] = 0x28;
    local_78 = 0;
    local_7a = 0x18;
    break;
  case 0x15:
  case 0x16:
    local_88[0] = 0x28;
    local_78 = 0;
    local_7a = 0x20;
    break;
  case 0x17:
    local_88[0] = 0x34;
    local_78 = 3;
    local_7a = 0x10;
    local_60 = 0xf800;
    local_5c = 0x7e0;
    local_58 = 0x1f;
    break;
  case 0x18:
    local_88[0] = 0x28;
    local_78 = 0;
    local_7a = 0x10;
    break;
  case 0x19:
    local_88[0] = 0x38;
    local_78 = 3;
    local_7a = 0x10;
    local_60 = 0x7c00;
    local_5c = 0x3e0;
    local_58 = 0x1f;
    local_54 = 0x8000;
    break;
  case 0x1a:
    local_88[0] = 0x38;
    local_78 = 3;
    local_7a = 0x10;
    local_60 = 0xf00;
    local_5c = 0xf0;
    local_58 = 0xf;
    local_54 = 0xf000;
    break;
  case 0x1b:
    local_88[0] = 0x28;
    local_78 = 0;
    local_7a = 8;
    local_c = (LPCVOID)0x400;
    do {
      uVar3 = local_14[uVar6 >> 5];
      iVar4 = uVar6 * 4;
      local_49c[iVar4 + 3] = 0;
      local_49c[iVar4 + 2] = uVar3;
      local_49c[iVar4 + 1] = local_14[uVar6 >> 2 & 7];
      uVar5 = uVar6 & 3;
      uVar6 = uVar6 + 1;
      local_49c[iVar4] = *(undefined1 *)((int)&local_8 + uVar5);
    } while (uVar6 < 0x100);
    break;
  default:
    return -0x7fffbffb;
  case 0x1d:
    local_60 = 0xe0;
    local_5c = 0x1c;
    local_58 = 3;
    goto LAB_0057ab3a;
  case 0x1e:
    local_88[0] = 0x34;
    local_78 = 3;
    local_7a = 0x10;
    local_60 = 0xf00;
    local_5c = 0xf0;
    local_58 = 0xf;
    break;
  case 0x1f:
    local_60 = 0x3ff;
    local_58 = 0x3ff00000;
    goto LAB_0057abcc;
  case 0x20:
    local_88[0] = 0x38;
    local_78 = 3;
    local_7a = 0x20;
    local_60 = 0xff;
    local_5c = 0xff00;
    local_58 = 0xff0000;
    local_54 = 0xff000000;
    break;
  case 0x21:
    local_88[0] = 0x34;
    local_78 = 3;
    local_7a = 0x20;
    local_60 = 0xff;
    local_5c = 0xff00;
    local_58 = 0xff0000;
    break;
  case 0x22:
    local_88[0] = 0x34;
    local_78 = 3;
    local_7a = 0x20;
    local_60 = 0xffff;
    local_5c = 0xffff0000;
    local_58 = 0;
    break;
  case 0x23:
    local_60 = 0x3ff00000;
    local_58 = 0x3ff;
LAB_0057abcc:
    local_88[0] = 0x38;
    local_78 = 3;
    local_7a = 0x20;
    local_5c = 0xffc00;
    local_54 = 0xc0000000;
  }
LAB_0057ad1c:
  local_88[1] = *(int *)((int)this + 0xc);
  local_88[2] = *(int *)((int)this + 0x10);
  uVar1 = local_7a >> 3;
  local_8c = local_88[1] * uVar1;
  local_10 = local_8c + 3 & 0xfffffffc;
  local_70 = 0xb12;
  local_6c = 0xb12;
  local_9a = local_88[2] * local_10 + local_88[0] + 0xe + (int)local_c;
  uStack_96 = 0;
  uStack_94 = 0;
  local_8 = local_88[0];
  nNumberOfBytesToWrite = (local_9a + 3U & 0xfffffffc) - local_9a;
  local_9a = nNumberOfBytesToWrite + local_9a;
  local_92 = local_88[0] + 0xe + (int)local_c;
  local_7c = 1;
  local_9c = 0x4d42;
  local_1c = this;
  if (param_2 != 0) {
    WriteFile(param_1,&local_9c,0xe,(LPDWORD)&param_2,(LPOVERLAPPED)0x0);
  }
  if (local_8 != 0) {
    WriteFile(param_1,local_88,local_8,(LPDWORD)&param_2,(LPOVERLAPPED)0x0);
  }
  if (local_c != (LPCVOID)0x0) {
    WriteFile(param_1,local_49c,(DWORD)local_c,(LPDWORD)&param_2,(LPOVERLAPPED)0x0);
  }
  local_8 = *(int *)((int)local_1c + 0x30);
  local_c = (LPCVOID)(*(int *)((int)local_1c + 0x1c) * local_8 +
                      *(int *)((int)local_1c + 0x18) * (uint)uVar1 + *(int *)((int)local_1c + 4));
  lpBuffer = (LPCVOID)((*(int *)((int)local_1c + 0x10) + -1) * local_8 + (int)local_c);
  if (local_c <= lpBuffer) {
    do {
      WriteFile(param_1,lpBuffer,local_8c,(LPDWORD)&param_2,(LPOVERLAPPED)0x0);
      if (local_8c < local_10) {
        WriteFile(param_1,&local_18,local_10 - local_8c,(LPDWORD)&param_2,(LPOVERLAPPED)0x0);
      }
      lpBuffer = (LPCVOID)((int)lpBuffer - *(int *)((int)local_1c + 0x30));
    } while (local_c <= lpBuffer);
  }
  if (nNumberOfBytesToWrite != 0) {
    WriteFile(param_1,&local_18,nNumberOfBytesToWrite,(LPDWORD)&param_2,(LPOVERLAPPED)0x0);
  }
  return 0;
}
