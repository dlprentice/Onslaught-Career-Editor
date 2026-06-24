/* address: 0x0056c724 */
/* name: ___Unk_0056c724 */
/* signature: void __cdecl ___Unk_0056c724(void * param_1) */


void __cdecl ___Unk_0056c724(void *param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 local_c [8];

  if (((param_1 == (void *)0x0) || (*(char *)param_1 == '\0')) ||
     (iVar1 = _strcmp(param_1,"ACP"), iVar1 == 0)) {
    uVar2 = 0x1004;
  }
  else {
    iVar1 = _strcmp(param_1,"OCP");
    if (iVar1 != 0) goto LAB_0056c780;
    uVar2 = 0xb;
  }
  iVar1 = (*DAT_009d0b38)(DAT_009d0b34,uVar2,local_c,8);
  if (iVar1 == 0) {
    return;
  }
  param_1 = local_c;
LAB_0056c780:
  CTexture__Helper_0055e21b(param_1);
  return;
}
