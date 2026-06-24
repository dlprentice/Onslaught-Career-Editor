/* address: 0x00441e50 */
/* name: CUnitAI__Unk_00441e50 */
/* signature: void __fastcall CUnitAI__Unk_00441e50(void * param_1) */


void __fastcall CUnitAI__Unk_00441e50(void *param_1)

{
  undefined4 *puVar1;
  undefined4 *obj;
  undefined4 *puVar2;
  undefined4 *puVar3;

  puVar1 = *(undefined4 **)param_1;
  do {
    do {
      obj = puVar1;
      if (obj == (undefined4 *)0x0) {
        return;
      }
      puVar1 = (undefined4 *)*obj;
    } while (obj == (undefined4 *)0x0);
    puVar2 = puVar1;
    puVar3 = DAT_0066ffb0;
    if (DAT_0066ffb0 != obj) {
      do {
        puVar2 = puVar3;
        if (puVar2 == (undefined4 *)0x0) break;
        puVar3 = (undefined4 *)*puVar2;
      } while ((undefined4 *)*puVar2 != obj);
      *puVar2 = puVar1;
      puVar2 = DAT_0066ffb0;
    }
    DAT_0066ffb0 = puVar2;
    OID__FreeObject(obj);
  } while( true );
}
