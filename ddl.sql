create table brand
(
    id   serial
        primary key,
    name varchar(32) not null
        unique
);

alter table brand
    owner to igor;

create table category
(
    id   serial
        primary key,
    name varchar(32) not null
        unique
);

alter table category
    owner to igor;

create table attribute
(
    id   serial
        primary key,
    name varchar(32) not null
        unique
);

alter table attribute
    owner to igor;

create table category_attribute
(
    id           serial
        primary key,
    category_id  integer not null
        constraint fk_category
            references category
            on delete cascade,
    attribute_id integer not null
        constraint fk_attribute
            references attribute
            on delete cascade,
    unique (category_id, attribute_id)
);

alter table category_attribute
    owner to igor;

create table product
(
    id           serial
        primary key,
    category_id  integer                                               not null
        constraint fk_category
            references category
            on delete cascade,
    brand_id     integer                                               not null
        constraint fk_brand
            references brand
            on delete cascade,
    sku          varchar(32)                                           not null
        unique,
    model        varchar,
    description  varchar,
    rrp          double precision default 0.0,
    create_date  timestamp        default CURRENT_TIMESTAMP,
    product_type varchar(8)       default 'product'::character varying not null
        constraint check_product_type
            check ((product_type)::text = ANY
                   ((ARRAY ['product'::character varying, 'service'::character varying])::text[]))
);

alter table product
    owner to igor;

create table product_attribute
(
    category_attribute_id integer     not null
        constraint fk_category_attribute
            references category_attribute
            on delete cascade,
    product_id            integer     not null
        constraint fk_product
            references product
            on delete cascade,
    name                  varchar(64) not null,
    unique (category_attribute_id, product_id)
);

alter table product_attribute
    owner to igor;

create table partner
(
    id                   serial
        primary key,
    name                 varchar(32) not null
        unique,
    default_incoterm     varchar(3)  default 'exw'::character varying
        constraint check_incoterms
            check ((default_incoterm)::text = ANY
                   ((ARRAY ['exw'::character varying, 'ddp'::character varying])::text[])),
    default_payment_term varchar(12) default 'on_invoice'::character varying
        constraint check_paymentterms
            check ((default_payment_term)::text = ANY
                   ((ARRAY ['on_invoice'::character varying, 'on_delivery'::character varying])::text[]))
);

alter table partner
    owner to igor;

create table contact
(
    id         serial
        primary key,
    partner_id integer                                           not null
        constraint fk_contact_partner
            references partner
            on delete cascade,
    type       varchar(8)   default 'contact'::character varying not null
        constraint check_contact_type
            check ((type)::text = ANY
                   ((ARRAY ['company'::character varying, 'delivery'::character varying, 'contact'::character varying])::text[])),
    address    varchar(255) default NULL::character varying,
    name       varchar(32)                                       not null,
    phone      varchar(16)  default NULL::character varying,
    constraint check_phone_or_address
        check ((address IS NOT NULL) OR (phone IS NOT NULL))
);

alter table contact
    owner to igor;

create table multiorder
(
    id            serial
        primary key,
    type          varchar(8)  default 'sale'::character varying  not null
        constraint check_type
            check ((type)::text = ANY ((ARRAY ['sale'::character varying, 'purchase'::character varying])::text[])),
    number        varchar(32)                                    not null
        unique,
    state         varchar(16) default 'draft'::character varying not null
        constraint check_state
            check ((state)::text = ANY
                   ((ARRAY ['draft'::character varying, 'done'::character varying, 'await_payment'::character varying, 'await_delivery'::character varying])::text[])),
    partner_id    integer                                        not null
        constraint fk_partner
            references partner
            on delete restrict,
    contact_id    integer                                        not null
        constraint fk_contact
            references contact
            on delete restrict,
    create_date   timestamp   default CURRENT_TIMESTAMP,
    deadline_date timestamp   default ('2022-12-05 10:15:26.367566'::timestamp without time zone + '1 mon'::interval),
    incoterm      varchar(3)  default 'exw'::character varying
        constraint check_incoterms
            check ((incoterm)::text = ANY ((ARRAY ['exw'::character varying, 'ddp'::character varying])::text[])),
    payment_term  varchar(16) default 'on_invoice'::character varying
        constraint check_paymentterms
            check ((payment_term)::text = ANY
                   ((ARRAY ['on_invoice'::character varying, 'on_delivery'::character varying])::text[]))
);

alter table multiorder
    owner to igor;

create table multimove
(
    id         serial
        primary key,
    order_id   integer                                not null
        constraint fk_order
            references multiorder
            on delete restrict,
    product_id integer                                not null
        constraint fk_product
            references product
            on delete restrict,
    unit_price double precision                       not null
        constraint check_unit_price
            check (unit_price >= (0)::double precision),
    sign       integer          default '-1'::integer not null
        constraint check_qty_sign
            check (sign = ANY (ARRAY [1, '-1'::integer])),
    qty_draft  double precision                       not null
        constraint check_qty_draft
            check (qty_draft > (0)::double precision),
    qty_done   double precision default 0,
    confirmed  boolean          default false         not null,
    unique (order_id, product_id)
);

alter table multimove
    owner to igor;

create table invoice
(
    id            serial
        primary key,
    invoice_type  varchar(16) default 'customer_invoice'::character varying not null
        constraint check_invoice_type
            check ((invoice_type)::text = ANY
                   ((ARRAY ['vendor_bill'::character varying, 'customer_invoice'::character varying])::text[])),
    number        varchar(32)                                               not null
        unique,
    order_id      integer                                                   not null
        constraint fk_invoice_order
            references multiorder,
    partner_id    integer                                                   not null
        constraint fk_invoice_partner
            references partner,
    contact_id    integer                                                   not null
        constraint fk_invoice_contact
            references contact,
    bank_id       integer                                                   not null,
    amount        double precision                                          not null,
    create_date   timestamp   default CURRENT_TIMESTAMP,
    deadline_date timestamp   default ('2022-12-05 10:16:35.283842'::timestamp without time zone + '1 mon'::interval),
    payed         boolean     default false
);

alter table invoice
    owner to igor;

create table bank
(
    id         serial
        primary key,
    partner_id integer     not null
        constraint fk_bank_partner
            references partner
            on delete cascade,
    iban       varchar(32) not null
        unique
);

alter table bank
    owner to igor;

create table test_detail
(
    id     serial
        primary key,
    d_mech integer     not null,
    d_code varchar(6)  not null,
    d_name varchar(32) not null
);

alter table test_detail
    owner to igor;

