-- =====================================================================
--  Tienda de ABAY: productos, stock y pedidos
--  Todas las tablas quedan cerradas (RLS sin políticas): solo la clave
--  service_role, que vive en las funciones del servidor, puede leerlas.
-- =====================================================================

create table if not exists tienda_producto (
  id          text primary key,
  nombre      text    not null,
  precio_cent integer not null check (precio_cent > 0),
  activo      boolean not null default true
);

create table if not exists tienda_stock (
  producto_id text    not null references tienda_producto(id) on delete cascade,
  talla       text    not null,
  unidades    integer not null default 0 check (unidades >= 0),
  primary key (producto_id, talla)
);

create table if not exists tienda_pedido (
  id            uuid primary key default gen_random_uuid(),
  ref           text not null unique,
  estado        text not null default 'pendiente'
                check (estado in ('pendiente','pagado','sin_stock','importe_mal','anulado')),
  metodo        text not null default 'tarjeta' check (metodo in ('tarjeta','bizum')),
  subtotal_cent integer not null,
  envio_cent    integer not null default 0,
  total_cent    integer not null,
  entrega       text not null check (entrega in ('recogida','envio')),

  nombre    text not null,
  email     text not null,
  telefono  text not null,
  direccion text,
  cp        text,
  poblacion text,
  provincia text,
  notas     text,

  ceca_referencia     text,
  ceca_num_aut        text,
  ceca_tipo_operacion text,
  ceca_final_pan      text,

  aviso_recibido_en timestamptz,
  pagado_en         timestamptz,
  creado_en         timestamptz not null default now(),
  ip                text
);

create index if not exists tienda_pedido_creado_idx on tienda_pedido (creado_en desc);
create index if not exists tienda_pedido_estado_idx on tienda_pedido (estado);

create table if not exists tienda_linea (
  id          bigserial primary key,
  pedido_id   uuid    not null references tienda_pedido(id) on delete cascade,
  producto_id text    not null,
  nombre      text    not null,
  talla       text    not null,
  unidades    integer not null check (unidades > 0),
  precio_cent integer not null
);

create index if not exists tienda_linea_pedido_idx on tienda_linea (pedido_id);

-- ajustes que se cambian sin tocar código
create table if not exists tienda_ajuste (
  clave text primary key,
  valor text
);

alter table tienda_producto enable row level security;
alter table tienda_stock    enable row level security;
alter table tienda_pedido   enable row level security;
alter table tienda_linea    enable row level security;
alter table tienda_ajuste   enable row level security;

-- =====================================================================
--  Confirmar un pedido cuando Cecabank avisa de que está cobrado.
--  Primero comprueba TODO el stock (bloqueando las filas) y solo
--  después descuenta, para no dejar un pedido a medias.
--  Devuelve: 'ok' | 'desconocido' | 'importe' | 'sin_stock'
-- =====================================================================
create or replace function confirmar_pedido(p_ref text, p_importe_cent integer)
returns text
language plpgsql
security definer
set search_path = public
as $$
declare
  v_pedido tienda_pedido%rowtype;
  v_linea  tienda_linea%rowtype;
  v_hay    integer;
begin
  select * into v_pedido from tienda_pedido where ref = p_ref for update;
  if not found then
    return 'desconocido';
  end if;

  -- si ya estaba cobrado, no volvemos a descontar: el aviso puede repetirse
  if v_pedido.estado = 'pagado' then
    return 'ok';
  end if;

  if v_pedido.total_cent <> p_importe_cent then
    update tienda_pedido set estado = 'importe_mal', aviso_recibido_en = now()
      where id = v_pedido.id;
    return 'importe';
  end if;

  -- 1) comprobar que hay de todo
  for v_linea in select * from tienda_linea where pedido_id = v_pedido.id loop
    select unidades into v_hay from tienda_stock
      where producto_id = v_linea.producto_id and talla = v_linea.talla
      for update;
    if not found or v_hay < v_linea.unidades then
      update tienda_pedido set estado = 'sin_stock', aviso_recibido_en = now()
        where id = v_pedido.id;
      return 'sin_stock';
    end if;
  end loop;

  -- 2) descontar
  for v_linea in select * from tienda_linea where pedido_id = v_pedido.id loop
    update tienda_stock set unidades = unidades - v_linea.unidades
      where producto_id = v_linea.producto_id and talla = v_linea.talla;
  end loop;

  update tienda_pedido
     set estado = 'pagado', pagado_en = now(), aviso_recibido_en = now()
   where id = v_pedido.id;

  return 'ok';
end;
$$;

revoke all on function confirmar_pedido(text, integer) from public, anon, authenticated;

-- =====================================================================
--  Datos de salida
-- =====================================================================
insert into tienda_producto (id, nombre, precio_cent) values
  ('camiseta-negra',  'Camiseta negra',  2999),
  ('camiseta-blanca', 'Camiseta blanca', 2999),
  ('tote',            'Tote bag',        1299)
on conflict (id) do nothing;

-- tirada de salida: 100 camisetas de cada color
insert into tienda_stock (producto_id, talla, unidades) values
  ('camiseta-negra','XS',5),  ('camiseta-negra','S',20),  ('camiseta-negra','M',25),
  ('camiseta-negra','L',30),  ('camiseta-negra','XL',15), ('camiseta-negra','XXL',5),
  ('camiseta-blanca','XS',5), ('camiseta-blanca','S',20), ('camiseta-blanca','M',25),
  ('camiseta-blanca','L',30), ('camiseta-blanca','XL',15),('camiseta-blanca','XXL',5),
  ('tote','U',50)   -- AJUSTAR: unidades reales de tote bags
on conflict (producto_id, talla) do nothing;

insert into tienda_ajuste (clave, valor) values
  ('envio_cent',  null),  -- PONER el importe del envío en céntimos (p.ej. '495').
                          -- Mientras esté vacío, la web solo ofrece recogida en el centro.
  ('envio_texto', 'Envío a España peninsular'),
  ('pedidos_abiertos', 'si')
on conflict (clave) do nothing;
