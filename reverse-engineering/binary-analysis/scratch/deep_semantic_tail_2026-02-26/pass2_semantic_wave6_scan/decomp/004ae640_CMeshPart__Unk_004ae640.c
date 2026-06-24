/* address: 0x004ae640 */
/* name: CMeshPart__Unk_004ae640 */
/* signature: void __fastcall CMeshPart__Unk_004ae640(int param_1) */


void __fastcall CMeshPart__Unk_004ae640(int param_1)

{
  void *pvVar1;
  int iVar2;

  if (*(void **)(param_1 + 0x104) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0x104));
    *(undefined4 *)(param_1 + 0x104) = 0;
  }
  if (*(void **)(param_1 + 0x108) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0x108));
    *(undefined4 *)(param_1 + 0x108) = 0;
  }
  if ((0 < *(int *)(param_1 + 0x90)) && (*(void **)(param_1 + 0x94) != (void *)0x0)) {
    OID__FreeObject(*(void **)(param_1 + 0x94));
    *(undefined4 *)(param_1 + 0x94) = 0;
  }
  if (*(void **)(param_1 + 0x134) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0x134));
  }
  if (*(int *)(param_1 + 0x84) != 0) {
    iVar2 = 0;
    if (0 < *(int *)(param_1 + 0xb4)) {
      do {
        pvVar1 = *(void **)(*(int *)(param_1 + 0x84) + iVar2 * 4);
        if (pvVar1 != (void *)0x0) {
          OID__FreeObject(pvVar1);
        }
        iVar2 = iVar2 + 1;
      } while (iVar2 < *(int *)(param_1 + 0xb4));
    }
    OID__FreeObject(*(void **)(param_1 + 0x84));
  }
  if (*(void **)(param_1 + 0x80) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0x80));
  }
  if (*(void **)(param_1 + 0xc4) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0xc4));
  }
  if (*(void **)(param_1 + 0x10c) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0x10c));
  }
  if (*(void **)(param_1 + 200) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 200));
  }
  if (*(void **)(param_1 + 0xcc) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0xcc));
  }
  if (*(void **)(param_1 + 0xd0) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0xd0));
  }
  if (*(int *)(param_1 + 0xd4) != 0) {
    iVar2 = 0;
    if (0 < *(int *)(param_1 + 0xac)) {
      do {
        OID__FreeObject(*(void **)(*(int *)(param_1 + 0xd4) + iVar2 * 4));
        iVar2 = iVar2 + 1;
      } while (iVar2 < *(int *)(param_1 + 0xac));
    }
    OID__FreeObject(*(void **)(param_1 + 0xd4));
  }
  if (*(int *)(param_1 + 0xd8) != 0) {
    iVar2 = 0;
    if (0 < *(int *)(param_1 + 0xac)) {
      do {
        OID__FreeObject(*(void **)(*(int *)(param_1 + 0xd8) + iVar2 * 4));
        iVar2 = iVar2 + 1;
      } while (iVar2 < *(int *)(param_1 + 0xac));
    }
    OID__FreeObject(*(void **)(param_1 + 0xd8));
  }
  pvVar1 = *(void **)(param_1 + 0x100);
  if (pvVar1 != (void *)0x0) {
    CInfluenceMap__Unk_004d3a00((int)pvVar1);
    OID__FreeObject(pvVar1);
  }
  if (*(void **)(param_1 + 0xfc) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0xfc));
    *(undefined4 *)(param_1 + 0xfc) = 0;
  }
  if (*(undefined4 **)(param_1 + 0x138) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)(param_1 + 0x138))(1);
    *(undefined4 *)(param_1 + 0x138) = 0;
  }
  return;
}
