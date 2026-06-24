/* address: 0x004ebd10 */
/* name: CStaticShadows__Unk_004ebd10 */
/* signature: void __fastcall CStaticShadows__Unk_004ebd10(void * param_1) */


void __fastcall CStaticShadows__Unk_004ebd10(void *param_1)

{
  int *obj;
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 *puVar4;
  int unaff_EDI;
  int iVar5;

  puVar4 = *(undefined4 **)param_1;
  do {
    if (puVar4 == (undefined4 *)0x0) {
      puVar4 = (undefined4 *)((int)param_1 + 0x18);
      iVar3 = 0x40;
      do {
        iVar5 = 0x40;
        do {
          if ((void *)*puVar4 != (void *)0x0) {
            OID__FreeObject((void *)*puVar4);
            *puVar4 = 0;
          }
          puVar4 = puVar4 + 1;
          iVar5 = iVar5 + -1;
        } while (iVar5 != 0);
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
      if (*(void **)((int)param_1 + 0x4018) != (void *)0x0) {
        OID__FreeObject(*(void **)((int)param_1 + 0x4018));
        *(undefined4 *)((int)param_1 + 0x4018) = 0;
      }
      return;
    }
    *puVar4 = 0;
    obj = *(int **)param_1;
    if (obj != (int *)0x0) {
      if (*obj != 0) {
        CStaticShadows__UpdateVisibility(*obj,1);
      }
      piVar2 = DAT_009c8010;
      if (DAT_009c8010 == obj) {
        DAT_009c8010 = (int *)obj[8];
      }
      else {
        do {
          piVar1 = piVar2;
          if (piVar1 == (int *)0x0) break;
          piVar2 = (int *)piVar1[8];
        } while ((int *)piVar1[8] != obj);
        piVar1[8] = obj[8];
      }
      if ((void *)obj[2] != (void *)0x0) {
        CStaticShadows__Unk_004ec250((void *)obj[2],(void *)0x3,unaff_EDI);
        obj[2] = 0;
      }
      OID__FreeObject(obj);
    }
    puVar4 = *(undefined4 **)param_1;
  } while( true );
}
