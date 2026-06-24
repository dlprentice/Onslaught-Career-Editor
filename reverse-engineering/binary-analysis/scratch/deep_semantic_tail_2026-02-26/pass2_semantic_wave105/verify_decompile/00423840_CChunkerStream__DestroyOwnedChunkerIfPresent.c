/* address: 0x00423840 */
/* name: CChunkerStream__DestroyOwnedChunkerIfPresent */
/* signature: void __fastcall CChunkerStream__DestroyOwnedChunkerIfPresent(int param_1) */


void __fastcall CChunkerStream__DestroyOwnedChunkerIfPresent(int param_1)

{
  void *obj;

  if ((*(int *)(param_1 + 0xc) != 0) && (obj = *(void **)(param_1 + 4), obj != (void *)0x0)) {
    CChunker__Destructor();
    OID__FreeObject(obj);
    *(undefined4 *)(param_1 + 4) = 0;
  }
  return;
}
