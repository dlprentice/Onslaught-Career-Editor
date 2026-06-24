/* address: 0x00560d2a */
/* name: CDXTexture__Unk_00560d2a */
/* signature: void __cdecl CDXTexture__Unk_00560d2a(void * param_1) */


void __cdecl CDXTexture__Unk_00560d2a(void *param_1)

{
  char cVar1;
  char cVar2;
  undefined *this;
  int iVar3;
  uint uVar4;
  uint unaff_ESI;
  undefined *puVar5;

  this = (undefined *)(int)*(char *)param_1;
  iVar3 = CTexture__Helper_005695af((int)this);
  if (iVar3 != 0x65) {
    do {
      param_1 = (void *)((int)param_1 + 1);
      if (DAT_00653a9c < 2) {
        uVar4 = (byte)PTR_DAT_00653890[*(char *)param_1 * 2] & 4;
        this = PTR_DAT_00653890;
      }
      else {
        puVar5 = (undefined *)0x4;
        uVar4 = CTexture__Helper_00563951(this,(int)*(char *)param_1,4,unaff_ESI);
        this = puVar5;
      }
    } while (uVar4 != 0);
  }
  cVar2 = *(char *)param_1;
  *(char *)param_1 = DAT_00653aa0;
  do {
    param_1 = (void *)((int)param_1 + 1);
    cVar1 = *(char *)param_1;
    *(char *)param_1 = cVar2;
    cVar2 = cVar1;
  } while (*(char *)param_1 != '\0');
  return;
}
