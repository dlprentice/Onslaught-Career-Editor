/* address: 0x0059778a */
/* name: CTexture__Helper_0059778a */
/* signature: int __stdcall CTexture__Helper_0059778a(void * param_1, void * param_2) */


/* WARNING: Removing unreachable block (ram,0x005977c1) */
/* WARNING: Removing unreachable block (ram,0x005977f0) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int CTexture__Helper_0059778a(void *param_1,void *param_2)

{
  float fVar1;
  int iVar2;
  float *pfVar3;
  uint uVar4;
  uint uVar5;

  iVar2 = CDXTexture__DecodeDxt1ColorBlockToRgba(param_1,(void *)((int)param_2 + 8));
  fVar1 = _DAT_005e9f28;
  if (-1 < iVar2) {
    uVar4 = *(uint *)param_2;
    iVar2 = 8;
    pfVar3 = (float *)((int)param_1 + 0xc);
    do {
      uVar5 = uVar4 & 0xf;
      uVar4 = uVar4 >> 4;
      *pfVar3 = (float)uVar5 * fVar1;
      pfVar3 = pfVar3 + 4;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
    uVar4 = *(uint *)((int)param_2 + 4);
    iVar2 = 8;
    pfVar3 = (float *)((int)param_1 + 0x8c);
    do {
      uVar5 = uVar4 & 0xf;
      uVar4 = uVar4 >> 4;
      *pfVar3 = (float)uVar5 * fVar1;
      pfVar3 = pfVar3 + 4;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
    iVar2 = 0;
  }
  return iVar2;
}
