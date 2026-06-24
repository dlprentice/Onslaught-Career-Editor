/* address: 0x005698e3 */
/* name: CDXTexture__Unk_005698e3 */
/* signature: int __cdecl CDXTexture__Unk_005698e3(void * param_1, void * param_2, void * param_3) */


int __cdecl CDXTexture__Unk_005698e3(void *param_1,void *param_2,void *param_3)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined1 local_1c [12];
  uint local_10;
  undefined4 local_c;
  int local_8;

  uVar1 = *(ushort *)((int)param_1 + 10);
  local_10 = *(uint *)((int)param_1 + 6);
  local_c = *(undefined4 *)((int)param_1 + 2);
  uVar3 = uVar1 & 0x7fff;
  iVar4 = uVar3 - 0x3fff;
  local_8 = (uint)*(ushort *)param_1 << 0x10;
  if (iVar4 == -0x3fff) {
    iVar4 = 0;
    iVar2 = CDXTexture__Helper_0056983b(&local_10);
    if (iVar2 != 0) {
LAB_00569a0f:
      iVar2 = 0;
      goto LAB_00569a11;
    }
    CDXTexture__Helper_0056982f(&local_10);
  }
  else {
    CDXTexture__Helper_00569814((int)local_1c,&local_10);
    iVar2 = CDXTexture__Helper_00569788((int)&local_10,*(int *)((int)param_3 + 8));
    if (iVar2 != 0) {
      iVar4 = uVar3 - 0x3ffe;
    }
    iVar2 = *(int *)((int)param_3 + 4);
    if (iVar4 < iVar2 - *(int *)((int)param_3 + 8)) {
      CDXTexture__Helper_0056982f(&local_10);
    }
    else {
      if (iVar2 < iVar4) {
        if (*(int *)param_3 <= iVar4) {
          CDXTexture__Helper_0056982f(&local_10);
          local_10 = local_10 | 0x80000000;
          CDXTexture__Unk_00569856(&local_10,*(uint *)((int)param_3 + 0xc));
          iVar4 = *(int *)((int)param_3 + 0x14) + *(int *)param_3;
          iVar2 = 1;
          goto LAB_00569a11;
        }
        local_10 = local_10 & 0x7fffffff;
        iVar4 = *(int *)((int)param_3 + 0x14) + iVar4;
        CDXTexture__Unk_00569856(&local_10,*(uint *)((int)param_3 + 0xc));
        goto LAB_00569a0f;
      }
      CDXTexture__Helper_00569814((int)&local_10,local_1c);
      CDXTexture__Unk_00569856(&local_10,iVar2 - iVar4);
      CDXTexture__Helper_00569788((int)&local_10,*(int *)((int)param_3 + 8));
      CDXTexture__Unk_00569856(&local_10,*(int *)((int)param_3 + 0xc) + 1);
    }
  }
  iVar4 = 0;
  iVar2 = 2;
LAB_00569a11:
  local_10 = iVar4 << (0x1fU - (char)*(undefined4 *)((int)param_3 + 0xc) & 0x1f) |
             -(uint)((uVar1 & 0x8000) != 0) & 0x80000000 | local_10;
  if (*(int *)((int)param_3 + 0x10) == 0x40) {
    *(uint *)((int)param_2 + 4) = local_10;
    *(undefined4 *)param_2 = local_c;
  }
  else if (*(int *)((int)param_3 + 0x10) == 0x20) {
    *(uint *)param_2 = local_10;
  }
  return iVar2;
}
