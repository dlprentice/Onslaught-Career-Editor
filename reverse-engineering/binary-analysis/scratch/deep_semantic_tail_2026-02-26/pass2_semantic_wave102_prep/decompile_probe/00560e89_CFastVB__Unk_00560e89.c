/* address: 0x00560e89 */
/* name: CFastVB__Unk_00560e89 */
/* signature: int __cdecl CFastVB__Unk_00560e89(void * param_1, int param_2, int param_3, void * param_4, int param_5) */


int __cdecl CFastVB__Unk_00560e89(void *param_1,int param_2,int param_3,void *param_4,int param_5)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  uint *puVar3;
  int iVar4;

  if ((char)param_5 != '\0') {
    CFastVB__Helper_0056112b
              ((void *)((uint)(*(int *)param_4 == 0x2d) + (int)param_1),(uint)(0 < param_2));
  }
  puVar1 = param_1;
  if (*(int *)param_4 == 0x2d) {
    *(undefined1 *)param_1 = 0x2d;
    puVar1 = (undefined1 *)((int)param_1 + 1);
  }
  puVar2 = puVar1;
  if (0 < param_2) {
    puVar2 = puVar1 + 1;
    *puVar1 = puVar1[1];
    *puVar2 = DAT_00653aa0;
  }
  puVar3 = CDXTexture__Helper_00567de0(puVar2 + param_2 + (uint)((char)param_5 == '\0'),"e+000");
  if (param_3 != 0) {
    *(undefined1 *)puVar3 = 0x45;
  }
  if (**(char **)((int)param_4 + 0xc) != '0') {
    iVar4 = *(int *)((int)param_4 + 4) + -1;
    if (iVar4 < 0) {
      iVar4 = -iVar4;
      *(undefined1 *)((int)puVar3 + 1) = 0x2d;
    }
    if (99 < iVar4) {
      *(char *)((int)puVar3 + 2) = *(char *)((int)puVar3 + 2) + (char)(iVar4 / 100);
      iVar4 = iVar4 % 100;
    }
    if (9 < iVar4) {
      *(char *)((int)puVar3 + 3) = *(char *)((int)puVar3 + 3) + (char)(iVar4 / 10);
      iVar4 = iVar4 % 10;
    }
    *(char *)(puVar3 + 1) = (char)puVar3[1] + (char)iVar4;
  }
  return (int)param_1;
}
